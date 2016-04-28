from opengever.base.marmoset_patch import marmoset_patch
from ZODB.POSException import ConflictError
import logging


LOGGER = logging.getLogger('opengever.base')


# Monkeypatch `OFS.CopySupport.CopyContainer._verifyObjectPaste`
# to disable `Delete objects` permission check when moving items

from Acquisition import aq_parent
from App.Dialogs import MessageDialog
from cgi import escape
from OFS.CopySupport import absattr
from OFS.CopySupport import CopyContainer
from OFS.CopySupport import CopyError


def _verifyObjectPaste(self, object, validate_src=1):
    # Verify whether the current user is allowed to paste the
    # passed object into self. This is determined by checking
    # to see if the user could create a new object of the same
    # meta_type of the object passed in and checking that the
    # user actually is allowed to access the passed in object
    # in its existing context.
    #
    # Passing a false value for the validate_src argument will skip
    # checking the passed in object in its existing context. This is
    # mainly useful for situations where the passed in object has no
    # existing context, such as checking an object during an import
    # (the object will not yet have been connected to the acquisition
    # heirarchy).

    if not hasattr(object, 'meta_type'):
        raise CopyError(MessageDialog(
              title   = 'Not Supported',
              message = ('The object <em>%s</em> does not support this' \
                         ' operation' % escape(absattr(object.id))),
              action  = 'manage_main'))

    if not hasattr(self, 'all_meta_types'):
        raise CopyError(MessageDialog(
              title   = 'Not Supported',
              message = 'Cannot paste into this object.',
              action  = 'manage_main'))

    method_name = None
    mt_permission = None
    meta_types = absattr(self.all_meta_types)

    for d in meta_types:
        if d['name'] == object.meta_type:
            method_name = d['action']
            mt_permission = d.get('permission')
            break

    if mt_permission is not None:
        sm = getSecurityManager()

        if sm.checkPermission(mt_permission, self):
            if validate_src:
                # Ensure the user is allowed to access the object on the
                # clipboard.
                try:
                    parent = aq_parent(aq_inner(object))
                except ConflictError:
                    raise
                except Exception:
                    parent = None

                if not sm.validate(None, parent, None, object):
                    raise Unauthorized(absattr(object.id))

                # --- Patch ---
                # Disable checking for `Delete objects` permission

                # if validate_src == 2: # moving
                #     if not sm.checkPermission(delete_objects, parent):
                #         raise Unauthorized('Delete not allowed.')

                # --- End Patch ---
        else:
            raise CopyError(MessageDialog(
                title = 'Insufficient Privileges',
                message = ('You do not possess the %s permission in the '
                           'context of the container into which you are '
                           'pasting, thus you are not able to perform '
                           'this operation.' % mt_permission),
                action = 'manage_main'))
    else:
        raise CopyError(MessageDialog(
            title = 'Not Supported',
            message = ('The object <em>%s</em> does not support this '
                       'operation.' % escape(absattr(object.id))),
            action = 'manage_main'))

CopyContainer._verifyObjectPaste = _verifyObjectPaste
LOGGER.info('Monkey patched OFS.CopySupport.CopyContainer._verifyObjectPaste')


# --------
# Marmoset patch `plone.app.upgrade.v43.betas.to43rc1` to delay an expensive
# upgrade. The upgrade is re-defined as opengever.policy.base.to4504.


from plone.app.upgrade.v43 import betas


def nullupgrade(context):
    pass

marmoset_patch(betas.to43rc1, nullupgrade)
LOGGER.info('Marmoset patched plone.app.upgrade.v43.betas.to43rc1')


# --------
# Monkey patch the regex used to replace relative paths in url() statements
# with absolute paths in the portal_css tool.
# This has been fixed as of release 3.0.3 of Products.ResourceRegistries
# which is only available for Plone 5.
# See https://github.com/plone/Products.ResourceRegistries/commit/4f9094919bc1c50404e74c748b067a3563e640aa

import re
from Products.ResourceRegistries import utils


utils.URL_MATCH = re.compile(r'''(url\s*\(\s*['"]?)(?!data:)([^'")]+)(['"]?\s*\))''', re.I | re.S)


LOGGER.info('Monkey patched Products.ResourceRegistries.utils.URL_MATCH regexp')


# --------
# Patch for Products.CMFEditions.historyidhandlertool
#           .HistoryIdHandlerTool.register
#
# The default "register" method uses the Products.CMFUid IUniqueIdGenerator
# utility for generating the history ID. This utility uses the auto-increment
# strategy, which generates a lot of conflicts.
#
# In order to reduce the conflicts when generating the history id,
# we switch to the uuid4 implementation, generating a random number instead
# and thus not writing to the same place.

from Products.CMFEditions.historyidhandlertool import HistoryIdHandlerTool
from uuid import uuid4


def HistoryIdHandlerTool_register(self, obj):
    uid = self.queryUid(obj, default=None)
    if uid is None:
        # generate a new unique id and set it
        uid = uuid4().int
        self._setUid(obj, uid)

    return uid


HistoryIdHandlerTool.register = HistoryIdHandlerTool_register
LOGGER.info('Monkey patched Products.CMFEditions.historyidhandlertool'
            '.HistoryIdHandlerTool.register')

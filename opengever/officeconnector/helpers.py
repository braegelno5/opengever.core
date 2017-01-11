from opengever.officeconnector.interfaces import IOfficeconnectorSettings
from plone import api
from plone.protect.utils import addTokenToUrl
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin  # noqa


def is_officeconnector_attach_enabled():
    return api.portal.get_registry_record(
        'attach_to_outlook_enabled', interface=IOfficeconnectorSettings)


def is_officeconnector_checkout_enabled():
    return api.portal.get_registry_record(
        'direct_checkout_and_edit_enabled', interface=IOfficeconnectorSettings)


def create_officeconnector_url(context, payload={}):
    if not (is_officeconnector_attach_enabled()
            or is_officeconnector_checkout_enabled()):
        return None

    if 'action' not in payload:
        return None

    plugin = None
    acl_users = getToolByName(context, "acl_users")
    plugins = acl_users._getOb('plugins')
    authenticators = plugins.listPlugins(IAuthenticationPlugin)

    # Assumes there is only one JWT auth plugin present!
    # This will work as long as the plugin this finds uses the same secret as
    # whatever it ends up authenticating against - this is in all likelihood
    # the Plone site keyring
    for id_, authenticator in authenticators:
        if authenticator.meta_type == "JWT Authentication Plugin":
            plugin = authenticator
            break

    if not plugin:
        return None

    payload['url'] = addTokenToUrl('/'.join([context.absolute_url(),
                                             payload['action']]))
    payload['filename'] = context.get_filename()

    user_id = api.user.get_current().getId()

    return 'officeconnector:' + plugin.create_token(user_id, data=payload)

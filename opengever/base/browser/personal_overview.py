from Products.CMFPlone.utils import getToolByName
from five import grok
from ftw.table import helper
from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.utils import get_client_id
from opengever.tabbedview.browser.tabs import Documents, Dossiers, Tasks
from opengever.tabbedview.browser.tabs import OpengeverListingTab
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingMixin
from zope.component import getUtility
from zope.interface import Interface


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


def remove_control_columns(columns):
    """Returns the control columns from list of columns and returns it back.
    """

    def _filterer(item):
        try:
            transform = item[1]
        except KeyError:
            return True
        else:
            if transform in (helper.draggable, helper.path_checkbox):
                return False
            else:
                return True

    return filter(_filterer, columns)


class PersonalOverview(TabbedView):
    """The personal overview view show all documents and dossier
    where the actual user is the responsible.
    """

    default_tabs = [
            {'id': 'mytasks', 'icon': None, 'url': '#', 'class': None},
            {'id': 'mydossiers', 'icon': None, 'url': '#', 'class': None},
            {'id': 'mydocuments', 'icon': None, 'url': '#', 'class': None},
            {'id': 'issuedtasks', 'icon': None, 'url': '#', 'class': None},
            ]

    admin_tabs = [
            {'id': 'alltasks', 'icon': None, 'url': '#', 'class': None},
            {'id': 'allissuedtasks', 'icon': None, 'url': '#', 'class': None},
        ]

    def get_tabs(self):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        is_admin = member and member.allowed(self.context,
                                             ('Administrator',))

        if is_admin:
            return self.default_tabs + self.admin_tabs
        else:
            return self.default_tabs


class MyDossiers(Dossiers):
    grok.name('tabbedview_view-mydossiers')
    grok.require('zope2.View')
    grok.context(Interface)

    types = ['opengever.dossier.businesscasedossier',
             'opengever.dossier.projectdossier',]

    search_options = {'responsible': authenticated_member,}

    enabled_actions = ['pdf_dossierlisting']
    major_actions = ['pdf_dossierlisting']

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]



class MyDocuments(Documents):
    grok.name('tabbedview_view-mydocuments')
    grok.require('zope2.View')
    grok.context(Interface)

    search_options = {'Creator': authenticated_member,
                      'isWorkingCopy': 0,
                      'trashed': False}

    enabled_actions = []
    major_actions = []
    columns = remove_control_columns(Dossiers.columns)

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class MyTasks(GlobalTaskListingMixin, OpengeverListingTab):
    """A listing view,
    wich show all task where the actual user is the responsible.

    This listing is based on opengever.globalindex (sqlalchemy) and respects
    the basic features of tabbedview such as searching and batching.
    """

    grok.name('tabbedview_view-mytasks')
    grok.require('zope2.View')
    grok.context(Interface)

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        portal_state = self.context.unrestrictedTraverse(
            '@@plone_portal_state')
        userid = portal_state.member().getId()

        query_util = getUtility(ITaskQuery)
        return query_util._get_tasks_for_responsible_query(userid,
                                                           self.sort_on,
                                                           self.sort_order)

class IssuedTasks(Tasks):
    """List all tasks where I'm the issuer and which are physically stored on
    the current client.
    """

    grok.name('tabbedview_view-issuedtasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = []
    major_actions = []
    columns = remove_control_columns(Dossiers.columns)

    search_options = {'issuer': authenticated_member,}


class AllTasks(MyTasks, OpengeverListingTab):
    """Lists all tasks assigned to this clients.
    Bases on MyTasks
    """

    grok.name('tabbedview_view-alltasks')
    grok.require('zope2.View')
    grok.context(Interface)

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        query_util = getUtility(ITaskQuery)
        return query_util._get_tasks_for_assigned_client_query(
            get_client_id(), self.sort_on, self.sort_order)


class AllIssuedTasks(Tasks):
    """List all tasks which are stored physically on this client.
    """

    grok.name('tabbedview_view-allissuedtasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = []
    major_actions = []
    columns = remove_control_columns(Dossiers.columns)

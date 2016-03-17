from AccessControl import Unauthorized
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.activity import is_activity_feature_enabled
from opengever.globalindex.model.task import Task
from opengever.latex.opentaskreport import is_open_task_report_allowed
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.tabbedview import LOG
from opengever.tabbedview import _
from opengever.tabbedview.browser.tabs import Documents, Dossiers
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from plone import api
from plone.memoize.view import memoize_contextless
from sqlalchemy.exc import OperationalError
from zope.interface import Interface
import AccessControl


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


def remove_subdossier_column(columns):
    """Removes the subdossier column from list of columns and returns it back.
    """

    def _filterer(item):
        if isinstance(
            item, dict) and item['column'] == 'containing_subdossier':
            return False
        return True

    return filter(_filterer, columns)


class PersonalOverview(TabbedView):
    """The personal overview view show all documents and dossier
    where the actual user is the responsible.
    """

    template = ViewPageTemplateFile("personal_overview.pt")

    default_tabs = [
        {'id': 'mydossiers', 'icon': None, 'url': '#', 'class': None},
        {'id': 'mydocuments', 'icon': None, 'url': '#', 'class': None},
        {'id': 'mytasks', 'icon': None, 'url': '#', 'class': None},
        {'id': 'myissuedtasks', 'icon': None, 'url': '#', 'class': None},
    ]

    admin_tabs = [
        {'id': 'alltasks', 'icon': None, 'url': '#', 'class': None},
        {'id': 'allissuedtasks', 'icon': None, 'url': '#', 'class': None},
        ]

    def __call__(self):
        """If user is not allowed to view PersonalOverview, redirect him
        to the repository root, otherwise behave like always.
        """
        user = AccessControl.getSecurityManager().getUser()
        if user == AccessControl.SecurityManagement.SpecialUsers.nobody:
            raise Unauthorized

        if not self.user_is_allowed_to_view():
            catalog = getToolByName(self.context, 'portal_catalog')
            repos = catalog(portal_type='opengever.repository.repositoryroot')
            repo_url = repos[0].getURL()
            return self.request.RESPONSE.redirect(repo_url)
        else:
            if is_open_task_report_allowed():
                # Somehow if only the pdf-open-task-report action is available
                # plone's `showEditableBorder` assumes that the edit-bar should
                # be hidden.
                # So we have to force the edit bar if the user can generate an
                # open task report.
                api.portal.get().REQUEST.set('enable_border', True)
            return self.template(self)

    def personal_overview_title(self):
        current_user = ogds_service().fetch_current_user()
        if current_user:
            user_name = current_user.label(with_principal=False)
        else:
            user_name = api.user.get_current().getUserName()

        return _('personal_overview_title',
                 default='Personal Overview: ${user_name}',
                 mapping=dict(user_name=user_name))

    def _is_user_admin(self):
        m_tool = getToolByName(self.context, 'portal_membership')
        member = m_tool.getAuthenticatedMember()
        if member:
            if member.has_role('Administrator') \
                    or member.has_role('Manager'):
                return True
        return False

    @property
    def notification_tabs(self):
        tabs = []
        if is_activity_feature_enabled():
            tabs.append(
                {'id': 'mynotifications',
                 'title': _('label_my_notifications', default=u'My notifications'),
                 'icon': None, 'url': '#', 'class': None})

        return tabs

    def get_tabs(self):
        tabs = self.default_tabs + self.notification_tabs
        if self.is_user_allowed_to_view_additional_tabs():
            tabs += self.admin_tabs

        return tabs

    def is_user_allowed_to_view_additional_tabs(self):
        """The additional tabs Alltasks and AllIssuedTasks are only shown
        to adminsitrators and users of the current inbox group."""

        inbox = get_current_org_unit().inbox()
        current_user = ogds_service().fetch_current_user()
        return current_user in inbox.assigned_users() or self._is_user_admin()

    @memoize_contextless
    def user_is_allowed_to_view(self):
        """Returns True if the current client is one of the user's home
        clients or an administrator and he therefore is allowed to view
        the PersonalOverview, False otherwise.
        """
        try:
            current_user = ogds_service().fetch_current_user()
            if get_current_admin_unit().is_user_assigned(current_user):
                return True
            elif self._is_user_admin():
                return True
        except OperationalError as e:
            LOG.exception(e)

        return False


class MyDossiers(Dossiers):
    grok.name('tabbedview_view-mydossiers')
    grok.require('zope2.View')
    grok.context(Interface)

    search_options = {'responsible': authenticated_member,
                      'is_subdossier': False}

    enabled_actions = [
        'pdf_dossierlisting',
        'export_dossiers',
        ]

    major_actions = ['pdf_dossierlisting']

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class MyDocuments(Documents):
    grok.name('tabbedview_view-mydocuments')
    grok.require('zope2.View')
    grok.context(Interface)

    search_options = {'Creator': authenticated_member,
                      'trashed': False}

    enabled_actions = [
        'zip_selected',
    ]
    major_actions = []

    columns = remove_subdossier_column(Documents.columns)

    @property
    def columns(self):
        """Gets the columns wich wich will be displayed
        """
        remove_columns = ['containing_subdossier']
        columns = []

        for col in super(MyDocuments, self).columns:
            if isinstance(col, dict) and \
                    col.get('column') in remove_columns:
                pass  # remove this column
            else:
                columns.append(col)

        return columns

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class MyTasks(GlobalTaskListingTab):
    """A listing view, which lists all tasks where the given
    user is responsible. It queries all admin units.

    This listing is based on opengever.globalindex (sqlalchemy) and respects
    the basic features of tabbedview such as searching and batching.
    """

    grok.name('tabbedview_view-mytasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = [
        'pdf_taskslisting',
        ]

    def get_base_query(self):
        portal_state = self.context.unrestrictedTraverse(
            '@@plone_portal_state')
        userid = portal_state.member().getId()

        return Task.query.users_tasks(userid)


class IssuedTasks(GlobalTaskListingTab):
    """A ListingView list all tasks where the given user is the issuer.
    Queries all admin units.
    """

    grok.name('tabbedview_view-myissuedtasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = ['pdf_taskslisting']

    def get_base_query(self):
        portal_state = self.context.unrestrictedTraverse(
            '@@plone_portal_state')
        userid = portal_state.member().getId()

        return Task.query.users_issued_tasks(userid)


class AllTasks(GlobalTaskListingTab):
    """Lists all tasks assigned to this clients.
    Bases on MyTasks
    """

    grok.name('tabbedview_view-alltasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = ['pdf_taskslisting']

    def get_base_query(self):
        return Task.query.by_assigned_org_unit(get_current_org_unit())


class AllIssuedTasks(GlobalTaskListingTab):
    """List all tasks which are stored physically on this client.
    """

    grok.name('tabbedview_view-allissuedtasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = ['pdf_taskslisting']

    def get_base_query(self):
        return Task.query.by_issuing_org_unit(get_current_org_unit())

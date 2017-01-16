from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.globalindex.model.task import Task
from opengever.meeting.committee import ICommittee
from opengever.meeting.tabs.meetinglisting import MeetingListingTab
from opengever.meeting.tabs.membershiplisting import MembershipListingTab
from opengever.meeting.tabs.submittedproposallisting import SubmittedProposalListingTab
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class Meetings(MeetingListingTab):
    grok.name('tabbedview_view-meetings')
    grok.context(ICommittee)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'start_datetime'

    enabled_actions = []
    major_actions = []


class SubmittedProposals(SubmittedProposalListingTab):
    grok.name('tabbedview_view-submittedproposals')
    grok.context(ICommittee)

    show_selects = False

    enabled_actions = []
    major_actions = []


class Memberships(MembershipListingTab):
    grok.name('tabbedview_view-memberships')
    grok.context(ICommittee)

    selection = ViewPageTemplateFile("templates/no_selection.pt")

    sort_on = 'member_id'

    enabled_actions = []
    major_actions = []

    def get_member_link(self, item, value):
        return item.member.get_link(aq_parent(aq_inner(self.context)))


class Tasks(GlobalTaskListingTab):
    grok.name('tabbedview_view-tasks')
    grok.context(ICommittee)

    enabled_actions = [
        'change_state',
        'pdf_taskslisting',
        'move_items',
        'export_tasks',
    ]

    major_actions = [
        'change_state',
    ]

    def get_base_query(self):
        return Task.query.by_container(self.context, get_current_admin_unit())

from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Proposal
from opengever.meeting.tabs.proposallisting import ProposalListingTab
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from zope.interface import implements
from zope.interface import Interface


def proposal_title_link(item, value):
    return item.get_submitted_link()


class ISubmittedProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for submitted proposal table source configs."""


class AllProposalFilter(Filter):

    visible_states = ['submitted', 'scheduled', 'decided']

    def update_query(self, query):
        return query.filter(Proposal.workflow_state.in_(self.visible_states))


class UndecidedProposalFilter(AllProposalFilter):

    visible_states = ['submitted', 'scheduled']


class DecidedProposalFilter(AllProposalFilter):

    visible_states = ['decided']


class SubmittedProposalListingTab(ProposalListingTab):
    implements(ISubmittedProposalTableSourceConfig)

    sort_on = 'title'

    filterlist_name = 'submitted_proposal_state_filter'
    filterlist_available = True

    filterlist = FilterList(
        AllProposalFilter('filter_proposals_all', _('all')),
        UndecidedProposalFilter(
            'filter_proposals_active',
            _('active'),
            default=True),
        DecidedProposalFilter('filter_proposals_decided', _('decided'))
    )

    def get_base_query(self):
        return Proposal.query.for_committee(self.context.load_model())

    @property
    def columns(self):
        """Inherit column definition from the ProposalListingTab,
        but replace transform with """

        columns = super(SubmittedProposalListingTab, self).columns
        for col in columns:
            if col.get('column') == 'title':
                col['transform'] = proposal_title_link

        return columns


class SubmittedProposalTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(SubmittedProposalListingTab, Interface)

    searchable_columns = [Proposal.title, ]

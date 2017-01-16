from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Proposal
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface


def proposal_link(item, value):
    return item.get_link()


def translated_state(item, value):
    wrapper = '<span class="wf-proposal-state-{0}">{1}</span>'
    return wrapper.format(
        item.get_state().title,
        translate(item.get_state().title, context=getRequest())
    )


def decision_number(item, value):
    agenda_item = item.agenda_item
    if not agenda_item:
        return u''

    decision_number = agenda_item.decision_number
    if not decision_number:
        return u''

    meeting = agenda_item.meeting
    if not meeting:
        return u''

    year = meeting.start.year
    return u'{} / {}'.format(year, decision_number)


class IProposalTableSourceConfig(ITableSourceConfig):
    """Marker interface for proposal table source configs."""


class ProposalListingTab(BaseListingTab):
    implements(IProposalTableSourceConfig)

    model = Proposal

    @property
    def columns(self):
        return (
            {'column': 'proposal_id',
             'column_title': _(u'label_proposal_id',
                               default=u'Reference Number')},

            {'column': 'decision_number',
             'column_title': _(u'label_decision_number',
                               default=u'Decision Number'),
             'transform': decision_number},

            {'column': 'title',
             'column_title': _(u'column_title', default=u'Title'),
             'transform': proposal_link},

            {'column': 'workflow_state',
             'column_title': _(u'column_state', default=u'State'),
             'transform': translated_state},

            {'column': 'committee_id',
             'column_title': _(u'column_comittee', default=u'Comittee'),
             'transform': lambda item, value: item.committee.get_link()},

            {'column': 'generated_meeting_link',
             'column_title': _(u'column_meeting', default=u'Meeting'),
             'transform': lambda item, value: item.get_meeting_link()},
        )


class ProposalTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(ProposalListingTab, Interface)

    searchable_columns = [Proposal.title, ]

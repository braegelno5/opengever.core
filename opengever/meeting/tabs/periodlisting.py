from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Period
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface


class IPeriodTableSourceConfig(ITableSourceConfig):
    """Marker interface for period table source configs."""


class PeriodListingTab(BaseListingTab):
    implements(IPeriodTableSourceConfig)

    model = Period
    sort_on = 'date_from'
    sort_reverse = True

    @property
    def columns(self):
        return (
            {'column': 'title',
             'column_title': _(u'column_title', default=u'Title'),
             },

            {'column': 'date_from',
             'column_title': _(u'column_date_from', default=u'Date from'),
             'transform': lambda item, value: item.get_date_from(),
             },

            {'column': 'date_to',
             'column_title': _(u'column_date_to', default=u'Date to'),
             'transform': lambda item, value: item.get_date_to(),
             },
            {'column': '',
             'transform': self.get_edit_link,
             },
            )

    def get_edit_link(self, item, value):
        url = item.get_edit_url(self.context)

        return '<a  href="{0}" title="{1}" class="edit_period">{1}</a>'.format(
                url, translate(_('label_edit', default=u'Edit'),
                               context=self.request))

    def get_base_query(self):
        return Period.query.by_committee(self.context.load_model())


class PeriodTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(PeriodListingTab, Interface)

    searchable_columns = [Period.title]
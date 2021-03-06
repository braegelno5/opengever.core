from opengever.base import _ as base_messagefactory
from opengever.base.viewlets.byline import BylineBase
from opengever.repository import _
from zope.i18n import translate


class RepositoryByline(BylineBase):

    @property
    def show_description(self):
        return bool(self.context.description)

    def get_description(self):
        return self.context.description

    def privacy_layer(self):
        return translate(self.context.privacy_layer,
                         context=self.request,
                         domain='opengever.base')

    def archival_value(self):
        return translate(self.context.get_archival_value(),
                         context=self.request,
                         domain='opengever.base')

    def get_items(self):
        return [
            {'class': 'review_state',
             'label': _('label_workflow_state', default='State'),
             'content': self.workflow_state(),
             'replace': False},

            {'class': 'privacy_layer',
             'label': base_messagefactory(u'label_privacy_layer',
                                          default=u'Privacy layer'),
             'content': self.privacy_layer(),
             'replace': False},

            {'class': 'archival_value',
             'label': base_messagefactory(u'label_archival_value',
                                          default=u'Archival value'),
             'content': self.archival_value(),
             'replace': False},
        ]


class RepositoryRootByline(BylineBase):
    def get_items(self):
        return []

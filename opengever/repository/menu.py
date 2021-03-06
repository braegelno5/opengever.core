from five import grok
from opengever.base.menu import FilteredPostFactoryMenu
from opengever.repository.interfaces import IRepositoryFolder
from zope.interface import Interface


class RepositoryFolderPostFactoryMenu(FilteredPostFactoryMenu):
    grok.adapts(IRepositoryFolder, Interface)

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'opengever.meeting.meetingdossier':
            return True

        if factory_id == u'opengever.dossier.businesscasedossier' and \
                not self.context.allow_add_businesscase_dossier:
            return True

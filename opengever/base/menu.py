from five import grok
from ftw.contentmenu.interfaces import IContentmenuPostFactoryMenu
from ftw.contentmenu.menu import CombinedActionsWorkflowMenu
from opengever.meeting import is_meeting_feature_enabled
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.interface import Interface


def order_factories(context, factories):
    """Orders the entries in the factory menu based on a hardcoded order.
    """

    factories_order = ['Document',
                       'Document with docucomposer',
                       'Document with docugate',
                       'document_with_template',
                       'document_from_officeatwork',
                       'Task',
                       'Add task from template',
                       'Mail',
                       'Subdossier',
                       'Participant',
                       'Business Case Dossier',
                       'Dossier with template',
                       'Disposition',
                       ]

    ordered_factories = []
    for factory_title in factories_order:
        try:
            factory = [f for f in factories if f.get(
                'title') == factory_title][0]
            ordered_factories.append(factory)
        except IndexError:
            pass

    remaining_factories = [
        f for f in factories if f.get('title') not in factories_order]

    all_factories = ordered_factories + remaining_factories
    return all_factories


class FilteredPostFactoryMenu(grok.MultiAdapter):
    """Build a customized factory menu by allowing factories to be filtered and
    renamed.

    Concrete filtering / renaming can be implemented by subclasses.
    """

    grok.adapts(Interface, Interface)
    grok.implements(IContentmenuPostFactoryMenu)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_filtered(self, factory):
        """Allows a subclass to determine whether a factory should be filtered
        (omitted) or not.
        """
        return False

    def rename(self, factory):
        """Lets a subclass rename a factory entry if necessary, and return the
        modified factory.
        """
        return factory

    def __call__(self, factories):
        filtered_factories = []
        for factory in factories:
            factory = self.rename(factory)

            if not self.is_filtered(factory):
                filtered_factories.append(factory)

        return order_factories(self.context, filtered_factories)


class PloneSitePostFactoryMenu(FilteredPostFactoryMenu):
    grok.adapts(IPloneSiteRoot, Interface)

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'opengever.meeting.committeecontainer':
            return not is_meeting_feature_enabled()

        return False


class OGCombinedActionsWorkflowMenu(CombinedActionsWorkflowMenu):

    def getWorkflowMenuItems(self, context, request):
        """ftw.contentmenu >= 2.2.2 does no longer protect the workflows
        "Advanced..." action with "Manage portal".
        We therefore just filter it.
        """

        result = (super(OGCombinedActionsWorkflowMenu, self)
                  .getWorkflowMenuItems(context, request))
        return filter(lambda item: (item.get('extra', {})
                                    .get('id', None) != 'advanced'), result)

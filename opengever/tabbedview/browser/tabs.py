from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile 
from Products.CMFCore.utils import getToolByName    
from ftw.tabbedview.browser.views import BaseListingView
from ftw.tabbedview.interfaces import ITabbedView
from five import grok
from ftw.table import helper

class OpengeverListingTab(grok.View, BaseListingView):
    grok.context(ITabbedView)
    grok.template('generic')
    
    update = BaseListingView.update
    
    columns = (
                ('', helper.draggable),
                ('', helper.path_checkbox),
                ('Title', 'sortable_title', helper.linked),
                ('modified', helper.readable_date), 
                ('Creator', helper.readable_author),
               )
    
    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]
        
        
    search_index = 'SearchableText' #only 'SearchableText' is implemented for now
    sort_on = 'modified'
    sort_order = 'reverse'    
    

class OpengeverTab(object):
    pass

class Documents(OpengeverListingTab):
    grok.name('tabbedview_view-documents')
    
    types = ['opengever.document.document',]
    
    search_options = {'isWorkingCopy':0}

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', helper.linked),
        ('document_author', 'document_author'),
        ('document_date', 'document_date', helper.readable_date),
        ('receipt_date', 'receipt_date', helper.readable_date),
        ('delivery_date', 'delivery_date', helper.readable_date),
        ('checked_out', 'checked_out')
        )
    
class Dossiers(OpengeverListingTab):
    grok.name('tabbedview_view-dossiers')
    
    types = ['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',]
    
    columns = (
                ('', helper.draggable),
                ('', helper.path_checkbox),
                ('reference_number'),
                ('Title', helper.linked),
                ('review_state'),
                ('responsible', helper.readable_author),
                ('start', helper.readable_date),
                ('end', helper.readable_date),
                
            )
    search_options = {'is_subdossier':False}
    
class SubDossiers(Dossiers):
    grok.name('tabbedview_view-subdossiers')
    search_options = {'is_subdossier':True}

class Tasks(OpengeverListingTab):
    grok.name('tabbedview_view-tasks')
    
    columns= (
                ('', helper.draggable),
                ('', helper.path_checkbox),
                ('Title', helper.linked),
                ('deadline', helper.readable_date),
                ('responsible', helper.readable_author),
                ('review_state'),
            )

    types = ['ftw.task.task',]
    
class Events(OpengeverListingTab):
    grok.name('tabbedview_view-events')

    types = ['dummy.event',]


#code below might go to opengover.dossier..     

from zope.annotation.interfaces import IAnnotations, IAnnotatable
from ftw.journal.interfaces import IAnnotationsJournalizable, IWorkflowHistoryJournalizable
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository.interfaces import IRepositoryFolder
from ftw.table.interfaces import ITableGenerator
from zope.component import queryUtility
from ftw.table import helper
        

class RepositoryOverview(grok.View, OpengeverTab):
    grok.context(IRepositoryFolder)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    #TODO: refactor view using viewlets
    def catalog(self, types):
        return self.context.portal_catalog(portal_type=types , 
                                            path=dict(depth=1, 
                                                      query='/'.join(self.context.getPhysicalPath())
                                                      ), 
                                                      sort_on='modified',
                                                      sort_order='reverse')

    def boxes(self):
        items = [
              dict(id = 'repostories', content=self.repostories()),
              dict(id = 'dossiers', content=self.dossiers()),
        ]
        return items

    def repostories(self):
        return self.catalog(['opengever.repository.repositoryfolder',])[:5]

    def dossiers(self):
        return self.catalog(['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',])[:5]

class DossierOverview(grok.View, OpengeverTab):
    grok.context(IDossierMarker)
    grok.name('tabbedview_view-overview')
    grok.template('overview')
    
    #TODO: refactor view using viewlets
    def catalog(self, types):
        return self.context.portal_catalog(portal_type=types , 
                                            path=dict(depth=1, 
                                                      query='/'.join(self.context.getPhysicalPath())
                                                      ), 
                                                      sort_on='modified',
                                                      sort_order='reverse') 

    def boxes(self):
        items = [[dict(id = 'subdossiers', content=self.subdossiers()),
                dict(id = 'tasks', content=self.tasks()),
                dict(id = 'journal', content=self.journal()),
                dict(id = 'sharing', content=self.sharing())],
                [dict(id = 'documents', content=self.documents()),]
        ]
        return items
                                                      
    def subdossiers(self):
        return self.catalog(['opengever.dossier.projectdossier', 'opengever.dossier.businesscasedossier',])[:5] 
                                            
    def tasks(self):
        return self.catalog(['ftw.task.task', ])[:5]  
    
    def documents(self): 
        return self.catalog(['opengever.document.document',] )[:10]                                        
    
    def events(self):
        return self.catalog(['dummy.event',] )[:5]     
                                            
    def journal(self):
        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(self.context)
            entries = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])[:5]
        elif IWorkflowHistoryJournalizable.providedBy(self.context):
            raise NotImplemented
        
        edict = [dict(Title=entry['action']['title'], getIcon='bullet_icon.gif ') for entry in reversed(entries)]
        return edict
    
    def sharing(self):
        # TODO: move to util
        role = 'Reader'
        results = []
        context = self.context
        pas_tool = getToolByName(context, 'acl_users')
        utils_tool = getToolByName(context, 'plone_utils')
        
        inherited_and_local_roles = utils_tool.getInheritedLocalRoles(context) + pas_tool.getLocalRolesForDisplay(context)

        for user_id_and_roles in inherited_and_local_roles:
            if user_id_and_roles[2] == 'user':
                if role in user_id_and_roles[1]:
                    user = pas_tool.getUserById(user_id_and_roles[0])
                    if user:
                        results.append(dict(
                                        Title = '%s (%s)' % (user.getProperty('fullname', ''), user.getId()), 
                                        getIcon='user.gif'
                                        ))
            if user_id_and_roles[2] == 'group':
                if role in user_id_and_roles[1]:
                    for user in pas_tool.getGroupById(user_id_and_roles[0]).getGroupMembers():
                        results.append(dict(
                                        Title = '%s (%s)' % (user.getProperty('fullname', ''), user.getId()), 
                                        getIcon='user.gif'
                                        ))
        return results


class Journal(grok.View, OpengeverTab):
     grok.context(IDossierMarker)
     grok.name('tabbedview_view-journal')
     grok.template('journal')

     def table(self):
         generator = queryUtility(ITableGenerator, 'ftw.tablegenerator') 
         columns = (('title', lambda x,y: x['action']['title']), 
                    'actor', 
                    ('time', helper.readable_date),
                    'comment'
                    )
         return generator.generate(reversed(self.data()), columns, css_mapping={'table':'journal-listing'})

     def data(self):
         context = self.context
         history = []

         if IAnnotationsJournalizable.providedBy(self.context):
             annotations = IAnnotations(context)
             return annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
         elif IWorkflowHistoryJournalizable.providedBy(self.context):
             raise NotImplemented

from plone.app.workflow.interfaces import ISharingPageRole
from zope.component import getUtilitiesFor, getMultiAdapter
from plone.app.workflow.browser.sharing import SharingView
from Acquisition import aq_inner

class Sharing(SharingView):
    
    template = ViewPageTemplateFile('tabs_templates/sharing.pt')

    def roles(self):
        """Get a list of roles that can be managed.

        Returns a list of dicts with keys:

            - id
            - title
        """
        context = aq_inner(self.context)
        portal_membership = getToolByName(context, 'portal_membership')

        pairs = []
        has_manage_portal = context.portal_membership.checkPermission('ManagePortal', context)
        aviable_roles_for_users = [ u'Editor',u'Reader', u'Contributor', u'Reviewer']
        for name, utility in getUtilitiesFor(ISharingPageRole):
            if not has_manage_portal and name not in aviable_roles_for_users:
                continue
            pairs.append(dict(id = name, title = utility.title))

        pairs.sort(key=lambda x: x["id"])
        return pairs


    def role_settings(self):
        context = self.context
        results = super(Sharing, self).role_settings()

        if not context.portal_membership.checkPermission('ManagePortal', context):
            results = [r for r in results if r['type']!='group']

        return results


    # @memoize
    # def roles(self):
    #     """Get a list of roles that can be managed.
    #     
    #     Returns a list of dicts with keys:
    #     
    #         - id
    #         - title
    #     """
    #     return [
    #         {
    #             'id'        : 'Reader',
    #             'title'     : 'read',
    #         },
    #         {
    #             'id'        : 'Editor',
    #             'title'     : 'write',
    #         },
    #     ]


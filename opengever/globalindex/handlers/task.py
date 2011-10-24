from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _mergedLocalRoles, getToolByName
from sqlalchemy.orm.exc import NoResultFound
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_client_id


def get_dossier_sequence_number(task):
    """Searches the first parental dossier relative to the task
    (breadcrumbs like) and returns its sequence number.
    """

    dossier_marker = 'opengever.dossier.behaviors.dossier.IDossierMarker'

    path = task.getPhysicalPath()[:-1]

    portal = getToolByName(task, 'portal_url').getPortalObject()
    portal_path = '/'.join(portal.getPhysicalPath())
    catalog = getToolByName(task, 'portal_catalog')

    while path and '/'.join(path) != portal_path:
        brains = catalog({'path': {'query': '/'.join(path),
                                   'depth': 0},
                          'object_provides': dossier_marker})

        if len(brains):
            if brains[0].sequence_number:
                return brains[0].sequence_number
            else:
                return ''
        else:
            path = aq_parent(aq_inner(path))

    return ''


def index_task(obj, event):
    """Index the given task in opengever.globalindex.
    """
    client_id = get_client_id()
    intids = getUtility(IIntIds)
    try:
        int_id = intids.getId(obj)
    except KeyError:
        # The intid event handler didn' create a intid for this object
        # yet. The event will be fired again after creating the id.
        return

    session = Session()
    try:
        task = session.query(Task).filter(Task.client_id==client_id).filter(
            Task.int_id==int_id).one()
    except NoResultFound:
        task = Task(int_id, client_id)
        session.add(task)

    task.title = obj.title


    # Generate and store the breadcrumb tooltip
    breadcrumb_titles = []
    breadcrumbs_view = getMultiAdapter((obj, obj.REQUEST),
                                       name='breadcrumbs_view')
    for elem in breadcrumbs_view.breadcrumbs():
        if isinstance(elem.get('Title'), unicode):
            breadcrumb_titles.append(elem.get('Title'))
        else:
            breadcrumb_titles.append(elem.get('Title').decode('utf-8'))

    task.breadcrumb_title = ' > '.join(breadcrumb_titles)

    url_tool = obj.unrestrictedTraverse('@@plone_tools').url()
    task.physical_path = '/'.join(url_tool.getRelativeContentPath(obj))
    task.review_state = obj.unrestrictedTraverse('@@plone_context_state').workflow_state()
    task.icon = obj.getIcon()
    task.responsible = obj.responsible
    task.issuer = obj.issuer

    # we need to have python datetime objects for make it work with sqlite etc.
    task.deadline = obj.deadline
    task.completed = obj.date_of_completion
    task.modified =  obj.modified().asdatetime().replace(tzinfo=None)

    task.task_type = obj.task_type
    task.sequence_number = getUtility(ISequenceNumber).get_number(obj)
    task.reference_number = IReferenceNumber(obj).get_number()

    # the dossier_sequence_number index is required for generating lists
    # of tasks as PDFs (LaTeX) as defined by the customer.
    task.dossier_sequence_number = get_dossier_sequence_number(obj)

    task.assigned_client = obj.responsible_client

    # index the predecessor
    if obj.predecessor:
        pred_client_id, pred_init_id = obj.predecessor.split(':', 1)
        try:
            predecessor = session.query(Task).filter_by(client_id=pred_client_id,
                                                    int_id=pred_init_id).one()
        except NoResultFound:
            # For some reason the referenced predecessor doesn't exist
            predecessor = None

    else:
        predecessor = None

    task.predecessor = predecessor

    # index the principal which have View permission. This is according to the
    # allowedRolesAndUsers index but it does not car of global roles.
    allowed_roles = rolesForPermissionOn(View, obj)
    principals = []
    for principal, roles in _mergedLocalRoles(obj).items():
        for role in roles:
            if role in allowed_roles:
                principals.append(principal.decode('utf-8'))
                break

    task.principals = principals

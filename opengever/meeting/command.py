from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.request import dispatch_json_request
from opengever.base.transport import REQUEST_KEY
from opengever.base.transport import Transporter
from opengever.meeting.model import SubmittedDocument
import json


class CreateSubmittedProposalCommand(object):

    def __init__(self, proposal):
        self.proposal = proposal
        self.submitted_proposal_path = None
        self.admin_unit_id = self.proposal.get_committee_admin_unit().id()

    def execute(self):
        model = self.proposal.load_model()
        jsondata = {'committee_oguid': model.committee.oguid.id,
                    'proposal_oguid': model.oguid.id}
        request_data = {REQUEST_KEY: json.dumps(jsondata)}
        response = dispatch_json_request(
            self.admin_unit_id, '@@create_submitted_proposal', data=request_data)
        self.submitted_proposal_path = response['path']


class CopyProposalDocumentCommand(object):
    """Copy documents attached to a proposal to the proposal's associated
    committee once a proposal is submitted.

    """
    def __init__(self, proposal, document, parent_action=None,
                 target_path=None, target_admin_unit_id=None):
        self.proposal = proposal
        self.document = document
        self._parent_action = parent_action
        self._target_path = target_path
        self._target_admin_unit_id = target_admin_unit_id

    @property
    def target_path(self):
        return self._target_path or self._parent_action.submitted_proposal_path

    @property
    def target_admin_unit_id(self):
        return self._target_admin_unit_id or self._parent_action.admin_unit_id

    def execute(self):
        reponse = self.copy_document(self.target_path, self.target_admin_unit_id)
        self.add_database_entry(reponse, self.target_admin_unit_id)

    def add_database_entry(self, reponse, target_admin_unit_id):
        oguid = Oguid.for_object(self.document)
        submitted_version = self.document.get_current_version()
        doc = SubmittedDocument(oguid=oguid,
                                proposal=self.proposal.load_model(),
                                submitted_admin_unit_id=target_admin_unit_id,
                                submitted_int_id=reponse['intid'],
                                submitted_physical_path=reponse['path'],
                                submitted_version=submitted_version)
        session = create_session()
        session.add(doc)

    def copy_document(self, target_path, target_admin_unit_id):
        return OgCopyCommand(
            self.document, target_admin_unit_id, target_path).execute()


class OgCopyCommand(object):

    def __init__(self, source, target_admin_unit_id, target_path):
        self.source = source
        self.target_path = target_path
        self.target_admin_unit_id = target_admin_unit_id

    def execute(self):
        return Transporter().transport_to(
            self.source, self.target_admin_unit_id, self.target_path)

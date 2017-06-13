from five import grok
from opengever.base.model import create_session
from opengever.base.security import elevated_privileges
from opengever.base.transport import PrivilegedReceiveObject
from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting.committee import ICommittee
from opengever.meeting.model import Proposal
import base64
import json


class CreateSubmittedProposal(PrivilegedReceiveObject):

    grok.context(ICommittee)
    grok.name('create_submitted_proposal')
    grok.require('zope2.Public')

    def receive(self):
        submitted_proposal = super(CreateSubmittedProposal, self).receive()

        if is_word_meeting_implementation_enabled():
            with elevated_privileges():
                data = json.loads(self.request['proposal_document'])
                submitted_proposal.create_proposal_document(
                    filename=data['file']['filename'],
                    content_type=data['file']['contentType'].encode('utf-8'),
                    data=base64.decodestring(data['file']['data']))

        return submitted_proposal

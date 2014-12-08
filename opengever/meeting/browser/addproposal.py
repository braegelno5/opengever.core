from five import grok
from opengever.meeting.form import MeetingModelAddForm
from opengever.meeting.proposal import Proposal
from plone.directives import dexterity
from z3c.form import field


class AddForm(MeetingModelAddForm, dexterity.AddForm):

    grok.name('opengever.meeting.proposal')
    content_type = Proposal
    fields = field.Fields(Proposal.model_schema)

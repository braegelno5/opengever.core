from BTrees.OOBTree import OOBTree
from opengever.base.date_time import utcnow_tz_aware
from opengever.meeting import _
from opengever.meeting.model import Meeting
from opengever.ogds.base.actor import Actor
from persistent.mapping import PersistentMapping
from plone import api
from uuid import uuid4
from zope.annotation.interfaces import IAnnotations


class ProposalHistory(object):
    """Adapter to keep track of a proposals history. Factory for new entries.

    Lists history records for an object and crates new ones. Records are stored
    in the objects annotations. Keeps a registry of supported history entries.

    History records are stored in the objects annotations with their timestamp
    as key and their data as value.
    """
    record_classes = {}
    annotation_key = 'object_history'

    @classmethod
    def register(cls, clazz):
        assert clazz.name not in cls.record_classes
        cls.record_classes[clazz.name] = clazz

    def __init__(self, context):
        self.context = context

    def __iter__(self):
        # fallback, old history entries, will mess up order, will go away
        for record in self.context.load_model().history_records:
            yield record

        history = self._get_history_for_reading()

        for key, val in reversed(history.items()):
            name = val.get('name')
            if not name:
                continue
            clazz = self.record_classes.get(name)
            if not clazz:
                continue

            yield clazz.re_populate(self.context, key, val)

    def append_record(self, name, timestamp=None, **kwargs):
        clazz = self.record_classes[name]

        history = self._get_history_for_writing()
        record = clazz(self.context, timestamp=timestamp, **kwargs)
        record.append_to(history)

        if record.needs_syncing:
            pass

        return record

    def receive_record(self, timestamp, data):
        history = self._get_history_for_writing()
        history[timestamp] = data

    def _get_history_for_writing(self):
        return IAnnotations(self.context).setdefault(
            self.annotation_key, OOBTree())

    def _get_history_for_reading(self):
        return IAnnotations(self.context).get(self.annotation_key, OOBTree())


class BaseHistoryRecord(object):
    """Basic implementation of a history record.

    Contains basic set of required data and abstract implementation. Can
    re-populate iself from data by invoking the __new__ method directly and
    then re-populating the attributeson the instance instead of calling
    __init__.

    """
    name = None
    needs_syncing = False

    @classmethod



    def __init__(self, context, timestamp=None):
        self.context = context
        self.timestamp = timestamp or utcnow_tz_aware()
        self.data = PersistentMapping(
            created=utcnow_tz_aware(),
            userid=api.user.get_current().getId(),
            name=self.name,
            id=uuid4())

    def append_to(self, history):
        if self.timestamp in history:
            return  # XXX raise?

        history[self.timestamp] = self.data

    def message(self):
        raise NotImplementedError

    @property
    def css_class(self):
        return self.name

    @property
    def created(self):
        return self.data['created']

    @property
    def text(self):
        return self.data.get('text')

    def get_actor_link(self):
        return Actor.lookup(self.data['userid']).get_link()


class ProposalCreated(BaseHistoryRecord):
    """A Proposal has been created."""

    name = 'created'

    def message(self):
        return _(u'proposal_history_label_created',
                 u'Created by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalCreated)


class ProposalSubmitted(BaseHistoryRecord):

    name = 'submitted'

    def message(self):
        return _(u'proposal_history_label_submitted',
                 u'Submitted by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalSubmitted)


class DocumentSubmitted(BaseHistoryRecord):

    name = 'document_submitted'
    css_class = 'documentAdded'

    def __init__(self, context, document_title, submitted_version,
                 timestamp=None):
        super(DocumentSubmitted, self).__init__(
            context, timestamp=timestamp)
        self.data['document_title'] = document_title
        self.data['submitted_version'] = submitted_version

    @property
    def document_title(self):
        return self.data.get('document_title')

    @property
    def submitted_version(self):
        return self.data.get('submitted_version')

    def message(self):
        return _(u'proposal_history_label_document_submitted',
                 u'Document ${title} submitted in version ${version} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'title': self.document_title or '',
                          'version': self.submitted_version})

ProposalHistory.register(DocumentSubmitted)


class ProposalRejected(BaseHistoryRecord):

    name = 'rejected'

    def __init__(self, context, text, timestamp=None):
        super(ProposalRejected, self).__init__(
            context, timestamp=timestamp)
        self.data['text'] = text

    def message(self):
        return _(u'proposal_history_label_rejected',
                 u'Rejected by ${user}',
                 mapping={'user': self.get_actor_link()})

ProposalHistory.register(ProposalRejected)


class ProposalScheduled(BaseHistoryRecord):

    name = 'scheduled'

    def __init__(self, context, meeting_id, timestamp=None):
        super(ProposalScheduled, self).__init__(
            context, timestamp=timestamp)
        self.data['meeting_id'] = meeting_id

    @property
    def meeting_title(self):
        meeting_id = self.data.get('meeting_id')
        meeting = Meeting.query.get(meeting_id)
        meeting_title = meeting.get_title() if meeting else u''
        return meeting_title

    def message(self):
        return _(u'proposal_history_label_scheduled',
                 u'Scheduled for meeting ${meeting} by ${user}',
                 mapping={'user': self.get_actor_link(),
                          'meeting': self.meeting_title})

ProposalHistory.register(ProposalScheduled)

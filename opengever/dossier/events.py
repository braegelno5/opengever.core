from opengever.dossier import interfaces
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class ParticipationCreated(ObjectEvent):
    """The `ParticipationCreated` is fired after a
    participation is created and added.
    """

    implements(interfaces.IParticipationCreated)

    def __init__(self, obj, participant):
        self.object = obj
        self.participant = participant


class ParticipationRemoved(ObjectEvent):
    """The `ParticipationRemoved` is fired before a participation is removed.
    """

    implements(interfaces.IParticipationRemoved)

    def __init__(self, obj, participant):
        self.object = obj
        self.participant = participant


class SourceFilesPurged(ObjectEvent):
    """The `SourceFilesErased` event is fired after the source files from
    all documents, as long they provide an archival file, contained by a
    dossier has been purged.
    """

    implements(interfaces.ISourceFilesPurged)

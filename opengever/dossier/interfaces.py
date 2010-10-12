from zope import schema
from zope.interface import Interface

class IDossierContainerTypes(Interface):
    """A type for collaborative spaces."""

    container_types = schema.List(
        title=u"container_types",
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.dossier.container_types',
        ),
    )

    maximum_dossier_depth = schema.Int(
        title=u'Maximum Dossier Depth',
        default=1
    )

    type_prefixes = schema.List(
        title=u"type_prefixes",
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.dossier.type_prefixes',
        ),
    )


class IConstrainTypeDecider(Interface):
    """ Adapter interface
    The constrain type decider decides, if a type is addable in the
    current dossier object. This decision depends on the current dossier
    type, the type to be added and the depth (distance to the next parent
    which is not an IDossier).
    Descriminators: ( request, context, FTI )
    * context : current dossier object
    * request
    * FTI: type to be added
    As Optional name the portal_type of the FTI can be used. If there is
    no such an adapter, the more general adapter without a name is used.
    """

    def __init__(self, context, request, fti):
        pass

    def addable(self, depth):
        """ Returns True, if a object of type *fti* can be created in the
        current *context*, depending on the *depth*
        """
        pass


class IDossierParticipants(Interface):
    """ Participants configuration (plone.registry)
    """

    roles = schema.List(
        title=u'Roles',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.dossier.participation_roles',
        ),
    )

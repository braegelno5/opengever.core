from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.base.sequence import SEQUENCE_NUMBER_ANNOTATION_KEY
from opengever.dossier.behaviors.dossiernamefromtitle import DossierNameFromTitle
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


class PathByParentsRefnum(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.reference_mapping = {}

    def __iter__(self):
        for item in self.previous:
            sequence_number = self.get_next_sequence_number(item.get('_type'))
            item['_path'] = '{}/{}'.format(
                self.get_parents_path(item['reference_number']),
                DossierNameFromTitle.format % sequence_number)

            yield item

    def get_next_sequence_number(self, portal_type):
        key = u'DefaultSequenceNumberGenerator.{}'.format(portal_type)
        annotations = IAnnotations(api.portal.get())
        map = annotations.get(SEQUENCE_NUMBER_ANNOTATION_KEY)
        if not map:
            raise Exception('Sequence Number not initialized yet.')
        return map.get(key, 1)

    def get_parents_path(self, reference_number):
        mapping = self.get_repository_mapping()
        return mapping[reference_number]

    def get_repository_mapping(self):
        if not self.reference_mapping:
            catalog = api.portal.get_tool('portal_catalog')
            repos = catalog(portal_type='opengever.repository.repositoryfolder')
            for repo in repos:
                number = repo.reference.split(' ')[-1]
                self.reference_mapping[number] = repo.getPath()

        return self.reference_mapping

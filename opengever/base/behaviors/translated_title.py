from collective.dexteritytextindexer import searchable
from opengever.base import _
from opengever.base.utils import get_preferred_language_code
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives.form import Schema
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.schema import TextLine


TRANSLATED_TITLE_NAMES = ('title_de', 'title_fr')


class ITranslatedTitleSupport(Interface):
    """Mark objects with translated title support."""


class TranslatedTitleMixin(object):
    """All types which use the translated title behavior need to extend
    this mixin.
    """

    def Title(self, language=None):
        title = ITranslatedTitle(self).translated_title(language)
        if isinstance(title, unicode):
            return title.encode('utf-8')
        return title or ''


class ITranslatedTitle(Schema):
    """Behavior schema adding translated title fields to dexterity
    content.
    """

    directives.order_before(title_de='*')
    searchable('title_de')
    title_de = TextLine(
        title=_(u'label_title_de', default=u'Title (German)'),
        required=True)

    directives.order_before(title_fr='*')
    searchable('title_fr')
    title_fr = TextLine(
        title=_(u'label_title_fr', default=u'Title (French)'),
        required=True)


alsoProvides(ITranslatedTitle, IFormFieldProvider)


class TranslatedTitle(object):

    FALLBACK_LANGUAGE = 'de'
    SUPPORTED_LANGUAGES = ['de', 'fr']

    def __init__(self, context):
        self.context = context

    def translated_title(self, language=None):
        if not language:
            language = get_preferred_language_code()

        title = getattr(self, 'title_{}'.format(language), None)
        if not title:
            title = getattr(self,
                            'title_{}'.format(self.FALLBACK_LANGUAGE), None)

        return title

    @property
    def title_de(self):
        return self.context.title_de

    @title_de.setter
    def title_de(self, value):
        if value is None:
            return
        if not isinstance(value, unicode):
            raise ValueError('title_de must be unicode.')
        self.context.title_de = value

    @property
    def title_fr(self):
        return self.context.title_fr

    @title_fr.setter
    def title_fr(self, value):
        if value is None:
            return
        if not isinstance(value, unicode):
            raise ValueError('title_fr must be unicode.')
        self.context.title_fr = value

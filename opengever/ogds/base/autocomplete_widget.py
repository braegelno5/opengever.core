from collective.elephantvocabulary.interfaces import IElephantVocabulary
from opengever.ogds.base.interfaces import IContactInformation
from plone.formwidget.autocomplete import widget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import ISource


class AutocompleteSelectionWidget(widget.AutocompleteSelectionWidget):

    @property
    def bound_source(self):
        if self._bound_source is None:
            source = self.source
            if IContextSourceBinder.providedBy(source):
                source = source(self.context)
            assert ISource.providedBy(source)

            # custom
            if IElephantVocabulary.providedBy(source):
                try:
                    # If we cannot adapt the behavior or schema interface,
                    # the context is wrong (e.g. we are one add form on the
                    # parent). So we skip adding the current value.
                    storage = self.field.interface(self.context)
                except TypeError:
                    value = None
                else:
                    value = getattr(storage, self.field.__name__)

                if value and value not in source.vocab:
                    contact_info = getUtility(IContactInformation)
                    term = source.vocab.createTerm(value, value,
                                                   contact_info.describe(value))
                    source.vocab._terms.append(term)
                    source.vocab.by_value[term.value] = term
                    source.vocab.by_token[term.token] = term
                    source.hidden_terms.append(value)
            # end custom
            self._bound_source = source
        return self._bound_source


@implementer(IFieldWidget)
def AutocompleteFieldWidget(field, request):
    return FieldWidget(field,
                       AutocompleteSelectionWidget(request))


class AutocompleteMultiSelectionWidget(widget.AutocompleteMultiSelectionWidget):

    @property
    def bound_source(self):
        if self._bound_source is None:
            source = self.source
            if IContextSourceBinder.providedBy(source):
                source = source(self.context)
            assert ISource.providedBy(source)

            # custom
            if IElephantVocabulary.providedBy(source):
                try:
                    # If we cannot adapt the behavior or schema interface,
                    # the context is wrong (e.g. we are one add form on the
                    # parent). So we skip adding the current value.
                    storage = self.field.interface(self.context)
                except TypeError:
                    value = None
                else:
                    value = getattr(storage, self.field.__name__)

                if value and value not in source.vocab:
                    contact_info = getUtility(IContactInformation)
                    term = source.vocab.createTerm(value, value,
                                                   contact_info.describe(value))
                    source.vocab._terms.append(term)
                    source.vocab.by_value[term.value] = term
                    source.vocab.by_token[term.token] = term
                    source.hidden_terms.append(value)
            # end custom
            self._bound_source = source
        return self._bound_source


@implementer(IFieldWidget)
def AutocompleteMultiFieldWidget(field, request):
    return FieldWidget(field,
                       AutocompleteMultiSelectionWidget(request))

from five import grok
from zope.interface import Interface


class View(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('gever-macros')

    template = grok.PageTemplateFile('templates/gever-macros.pt')

    def __getitem__(self, key):
        return self.template._template.macros[key]

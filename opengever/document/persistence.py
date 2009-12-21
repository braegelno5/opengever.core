import md5
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface

from five import grok
from persistent.dict import PersistentDict
from Products.CMFPlone.interfaces import IPloneSiteRoot
from datetime import datetime, timedelta

from Acquisition import aq_inner


class IDCQueue(Interface):
    pass


class DCQueue(grok.adapter):
    grok.context(IPloneSiteRoot)
    grok.implements(IDCQueue)

    def __init__(self, context):
        self.context = aq_inner(context.portal_url.getPortalObject())
        self.annotation = IAnnotations(self.context)
        self.key = "opengever.docucomposer.document"

    def appendDCDoc(self, dcAttr):
        if not isinstance(dcAttr, PersistentDict):
            raise TypeError()
        dcdict = self.getDCDocs()

        # token erstellen
        token = md5.new(str(datetime.now())).hexdigest()
        while dcdict.get(token, None):
            token = md5.new(str(datetime.today() + timedelta(5))).digest()

        dcdict.__setitem__(token, dcAttr)
        self._setDCDoc(dcdict)
        return token

    def removeDCDoc(self, key):
        dict = self.getDCDocs()
        dict.__delitem__(self, key)
        self._setDCDocs(dict)

    def _setDCDoc(self, dcdict):
        if not isinstance(dcdict, PersistentDict):
            raise TypeError('Excpected PersistentDict')
        self.annotation[self.key] = dcdict

    def getDCDocs(self):
        return self.annotation.get(self.key, PersistentDict())

    def clearUP(self):
        # XXX TODO
        pass

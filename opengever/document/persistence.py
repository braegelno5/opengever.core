from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
from zope.component import getUtility

from five import grok
from persistent.dict import PersistentDict
from Products.CMFPlone.interfaces import IPloneSiteRoot
from DateTime import DateTime
from plone.keyring.interfaces import IKeyManager

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
        dcdict = self.getDCDocs()
        
        persdata = PersistentDict(dcAttr)
        
        # token erstellen
        token = getUtility(IKeyManager).secret()
        token = token.encode('hex')

        dcdict.__setitem__(token, persdata)
        self._setDCDoc(dcdict)
        return token

    def removeDCDoc(self, key):
        dict = self.getDCDocs()
        dict.__delitem__(key)
        self._setDCDoc(dict)

    def _setDCDoc(self, dcdict):
        if not isinstance(dcdict, PersistentDict):
            raise TypeError('Excpected PersistentDict')
        self.annotation[self.key] = dcdict

    def getDCDocs(self):
        return self.annotation.get(self.key, PersistentDict())

    def clearUp(self):
        dc_dict = self.getDCDocs()
        data = dc_dict.data
        for item in data:
            dict = data[item]
            if dict['creation_date'] < (DateTime() -1):
                self.removeDCDoc(item)
        pass

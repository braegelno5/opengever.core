"""eCH-0147T2 model"""
from Products.CMFCore.utils import getToolByName
from opengever.ech0147.bindings import ech0147t0
from opengever.ech0147.bindings import ech0147t1
from opengever.ech0147.bindings import ech0039
from opengever.ech0147.bindings import ech0058
from opengever.ech0147.utils import file_checksum
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.dossier import IDossier
from uuid import uuid4
from datetime import datetime
from pyxb.utils.domutils import BindingDOMSupport
import os.path

BindingDOMSupport.DeclareNamespace(ech0147t1.Namespace, 'eCH-0147T1')
BindingDOMSupport.DeclareNamespace(ech0147t0.Namespace, 'eCH-0147T0')
BindingDOMSupport.DeclareNamespace(ech0039.Namespace, 'eCH-0039')
BindingDOMSupport.DeclareNamespace(ech0058.Namespace, 'eCH-0058')


class Message(object):
    """eCH-0147T1 message"""

    def __init__(self):
        self.directive = None
        self.dossiers = []
        self.documents = []
        self.addresses = []

    def add_object(self, obj):
        if IDossierMarker.providedBy(obj):
            self.dossiers.append(Dossier(obj, u'files'))
        elif IDocumentSchema.providedBy(obj):
            self.documents.append(Document(obj, u'files'))

    def binding(self):
        """Return XML binding"""
        m = ech0147t1.message()
        m.header = self.header()
        m.content_ = ech0147t1.contentType()
        if self.directive is not None:
            m.content_.directive = self.directive.binding()

        if self.dossiers:
            m.content_.dossiers = ech0147t0.dossiersType()
            for dossier in self.dossiers:
                m.content_.dossiers.append(dossier.binding())

        if self.documents:
            m.content_.documents = ech0147t0.documentsType()
            for document in self.documents:
                m.content_.append(document.binding())

        if self.addresses:
            m.content_.addresses = ech0147t0.adressesType()
            for address in self.addresses:
                m.content_.append(address.binding())

        return m

    def header(self):
        h = ech0147t0.headerType()
        h.senderId = u'gever@onegovgever.ch'
        h.messageId = unicode(uuid4())
        h.messageType = 1
        h.messageGroup = ech0039.messageGroupType(1, 1)
        h.sendingApplication = ech0058.sendingApplicationType(
            u'4teamwork AG', u'OneGov GEVER', u'3.7')
        h.messageDate = datetime.now()
        h.action = 1
        h.testDeliveryFlag = False
        return h

    def add_to_zip(self, zipfile):
        for dossier in self.dossiers:
            dossier.add_to_zip(zipfile)
        for document in self.documents:
            zipfile.write(document.blobpath, document.path)


DOSSIER_STATUS_MAPPING = {
    u'dossier-state-active': u'in_process',
    u'dossier-state-archived': u'archived',
    u'dossier-state-inactive': u'canceled',
    u'dossier-state-resolved': u'closed',
    u'dossier-state-offered': u'in_selection',
}


class Dossier(object):

    def __init__(self, obj, base_path):
        self.obj = obj
        self.path = os.path.join(base_path, self.obj.getId())

        self.dossiers = []
        self.documents = []
        self.folders = []

        self._add_descendants()

    def _add_descendants(self):
        objs = self.obj.objectValues()
        for obj in objs:
            if IDossierMarker.providedBy(obj):
                self.dossiers.append(Dossier(obj, self.path))
            elif IDocumentSchema.providedBy(obj):
                self.documents.append(Document(obj, self.path))

    def binding(self):
        d = ech0147t0.dossierType()
        d.uuid = self.obj.UID()

        wftool = getToolByName(self.obj, "portal_workflow")
        status = wftool.getInfoFor(self.obj, 'review_state')
        d.status = DOSSIER_STATUS_MAPPING[status]
        d.titles = ech0039.titlesType()
        d.titles.append(ech0039.titleType(self.obj.Title().decode('utf8'), lang=u'DE'))
        # d.classification = ech0039.classificationType()
        # d.hasPrivacyProtection = False
        dossier_obj = IDossier(self.obj)
        d.openingDate = dossier_obj.start

        if self.dossiers:
            d.dossiers = ech0147t0.dossiersType()
            for dossier in self.dossiers:
                d.dossiers.append(dossier.binding())

        if self.documents:
            d.documents = ech0147t0.documentsType()
            for document in self.documents:
                d.documents.append(document.binding())

        return d

    def add_to_zip(self, zipfile):
        for dossier in self.dossiers:
            dossier.add_to_zip(zipfile)
        for document in self.documents:
            zipfile.write(document.blobpath, document.path)


class Document(object):

    def __init__(self, obj, base_path):
        self.obj = obj
        self.path = os.path.join(base_path, self.obj.file.filename)
        self.blobpath = self.obj.file._blob.committed()

    def binding(self):
        d = ech0147t0.documentType()
        d.uuid = self.obj.UID()
        d.titles = ech0039.titlesType()
        d.titles.append(ech0039.titleType(
            self.obj.Title().decode('utf8'), lang=u'DE'))
        d.status = u'undefined'
        d.files = ech0147t0.filesType()
        f = ech0147t0.fileType()
        f.pathFileName = self.path
        f.mimeType = self.obj.file.contentType
        f.hashCodeAlgorithm, f.hashCode = file_checksum(self.blobpath)
        d.files.append(f)

        return d

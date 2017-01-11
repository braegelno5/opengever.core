from opengever.document.document import IDocumentSchema
from opengever.officeconnector.helpers import create_officeconnector_url
from Products.Five import BrowserView
from zExceptions import NotFound


class OfficeconnectorAttachURLView(BrowserView):

    def __call__(self):
        if not IDocumentSchema.providedBy(self.context):
            raise NotFound
        payload = {'action': 'attach'}
        return create_officeconnector_url(self.context, payload=payload)


class OfficeconnectorCheckoutURLView(BrowserView):

    def __call__(self):
        if not IDocumentSchema.providedBy(self.context):
            raise NotFound
        payload = {'action': 'checkout'}
        return create_officeconnector_url(self.context, payload=payload)

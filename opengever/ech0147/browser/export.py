from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from opengever.ech0147 import model
from tempfile import TemporaryFile
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile
from ZPublisher.Iterators import IStreamIterator
from zope.interface import implements


class ECH0147ExportView(BrowserView):

    def __call__(self):

        catalog = getToolByName(self.context, 'portal_catalog')
        items = catalog(portal_type='opengever.dossier.businesscasedossier',)
        message = model.Message()
        for item in items:
            message.add_object(item.getObject())

        header_dom = message.header().toDOM(element_name='eCH-0147T0:header')
        message_dom = message.binding().toDOM()

        # body = message_dom.toprettyxml(encoding='UTF-8')
        # response = self.request.response
        # response.setHeader(
        #     "Content-Disposition", 'inline; filename="metadata.xml"')
        # response.setHeader("Content-type", "text/xml")
        # response.setHeader("Content-Length", len(body))
        # return body

        tmpfile = TemporaryFile()
        with ZipFile(tmpfile, 'w', ZIP_DEFLATED, True) as zipfile:
            zipfile.writestr('header.xml', header_dom.toprettyxml(encoding='UTF-8'))
            zipfile.writestr('message.xml', message_dom.toprettyxml(encoding='UTF-8'))
            message.add_to_zip(zipfile)

        size = tmpfile.tell()

        response = self.request.response
        response.setHeader(
            "Content-Disposition",
            'inline; filename="message.zip"')
        response.setHeader("Content-type", "application/zip")
        response.setHeader("Content-Length", size)

        return TempfileStreamIterator(tmpfile, size)


class TempfileStreamIterator(object):

    implements(IStreamIterator)

    def __init__(self, tmpfile, size, chunksize=1 << 16):
        self.size = size
        tmpfile.seek(0)
        self.file = tmpfile
        self.chunksize = chunksize

    def next(self):
        data = self.file.read(self.chunksize)
        if not data:
            self.file.close()
            raise StopIteration
        return data

    def __len__(self):
        return self.size

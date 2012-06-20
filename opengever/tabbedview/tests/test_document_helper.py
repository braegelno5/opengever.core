from ftw.testing import MockTestCase
from mocker import ANY
from opengever.tabbedview.utils import get_containg_document_tab_url
from opengever.task.task import ITask


class TestDocumentsUrl(MockTestCase):

    def test_task(self):
        document = self.stub()
        folder = self.providing_stub([ITask])
        tool = self.stub()
        self.set_parent(document, folder)
        self.expect(folder.absolute_url()).result('http://nohost/plone/folder')
        self.mock_tool(tool, 'portal_membership')
        self.expect(tool.checkPermission(ANY, ANY)).result(True)
        self.replay()
        url = get_containg_document_tab_url(document)
        self.assertEqual(url, 'http://nohost/plone/folder#relateddocuments')

    def test_dossier(self):
        document = self.stub()
        folder = self.stub()
        tool = self.stub()
        self.set_parent(document, folder)
        self.expect(folder.absolute_url()).result('http://nohost/plone/folder')
        self.mock_tool(tool, 'portal_membership')
        self.expect(tool.checkPermission(ANY, ANY)).result(True)
        self.replay()
        url = get_containg_document_tab_url(document)
        self.assertEqual(url, 'http://nohost/plone/folder#documents')
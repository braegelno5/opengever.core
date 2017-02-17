from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.mail import IMail
from ftw.testing import freeze
from opengever.document.document import IDocumentSchema
from opengever.document.maintenance import DocumentMaintenance
from opengever.testing import FunctionalTestCase


class TestDocumentMaintenance(FunctionalTestCase):

    def test_get_dossiers_to_erase_returns_all_dossiers(self):
        dossier_a = create(Builder('dossier')
                           .having(end=date(2016, 1, 2)))
        dossier_b = create(Builder('dossier')
                           .having(end=date(2015, 2, 1)))
        dossier_c = create(Builder('dossier')
                           .having(end=date(2013, 5, 12)))

        with freeze(datetime(2017, 3, 5)):
            self.assertItemsEqual(
                [dossier_c],
                DocumentMaintenance().get_dossiers_to_erase())


class TestSourceFilePurgement(FunctionalTestCase):

    def test_get_documents_to_erase_returns_only_docs_with_expired_waiting_period(self):
        dossier_a = create(Builder('dossier')
                           .having(end=date(2015, 2, 1)))
        document_a = create(Builder('document')
                            .attach_archival_file_containing('DATA')
                            .within(dossier_a))
        dossier_b = create(Builder('dossier')
                           .having(end=date(2013, 5, 12)))
        document_b = create(Builder('document')
                            .attach_archival_file_containing('DATA')
                            .within(dossier_b))
        document_c = create(Builder('document')
                            .attach_archival_file_containing('DATA')
                            .within(dossier_b))

        with freeze(datetime(2017, 3, 5)):
            self.assertItemsEqual(
                [document_b, document_c],
                DocumentMaintenance().get_documents_to_erase_source_file())

    def test_get_documents_to_erase_returns_only_docs_with_archival_file(self):
        dossier = create(Builder('dossier')
                         .having(end=date(2013, 5, 12)))
        document_a = create(Builder('document')
                            .attach_file_containing('DATA')
                            .attach_archival_file_containing('DATA')
                            .within(dossier))
        document_b = create(Builder('document')
                            .attach_file_containing('DATA')
                            .within(dossier))

        with freeze(datetime(2017, 3, 5)):
            self.assertItemsEqual(
                [document_a],
                DocumentMaintenance().get_documents_to_erase_source_file())

    def test_purge_source_files_sets_file_to_none_for_documents(self):
        dossier = create(Builder('dossier')
                         .having(end=date(2013, 5, 12)))
        document_a = create(Builder('document')
                            .attach_file_containing('DATA')
                            .attach_archival_file_containing('DATA')
                            .within(dossier))
        document_b = create(Builder('document')
                            .attach_file_containing('DATA')
                            .within(dossier))

        with freeze(datetime(2017, 3, 5)):
            DocumentMaintenance().purge_source_files()

        self.assertIsNone(IDocumentSchema(document_a).file)
        self.assertIsNotNone(IDocumentSchema(document_b).file)

    def test_purge_source_files_sets_message_to_none_for_mails(self):
        dossier = create(Builder('dossier')
                         .having(end=date(2013, 5, 12)))
        mail_a = create(Builder('mail')
                        .with_dummy_message()
                        .attach_archival_file_containing('DATA')
                        .within(dossier))
        mail_b = create(Builder('mail')
                        .with_dummy_message()
                        .within(dossier))

        with freeze(datetime(2017, 3, 5)):
            DocumentMaintenance().purge_source_files()

        self.assertIsNone(IMail(mail_a).message)
        self.assertIsNotNone(IMail(mail_b).message)

from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import FunctionalTestCase
import transaction


class TestRetentionExpirationDate(FunctionalTestCase):

    def setUp(self):
        super(TestRetentionExpirationDate, self).setUp()
        self.dossier = create(Builder('dossier')
                              .having(end=date(2010, 02, 21),
                                      retention_period=20))

    def test_is_the_retention_period_years_added_to_the_end_date(self):
        self.assertEqual(date(2030, 02, 21),
                         self.dossier.get_retention_expiration_date())

    @browsing
    def test_is_updated_when_resolving_a_dossier(self, browser):
        with freeze(datetime(2010, 02, 21)):
            IDossier(self.dossier).end = date(2010, 02, 25)
            transaction.commit()

            browser.login().open(self.dossier)
            browser.find('dossier-transition-deactivate').click()
            self.assertEqual(date(2030, 02, 25),
                             self.dossier.get_retention_expiration_date())

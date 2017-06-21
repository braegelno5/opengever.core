from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.meeting.model import Committee
from opengever.testing import FunctionalTestCase
import transaction


class TestCommitteeWorkflow(FunctionalTestCase):

    def test_initial_state_is_active(self):
        committee = create(Builder('committee').titled(u'My Committee'))
        self.assertEqual(Committee.STATE_ACTIVE,
                         committee.load_model().get_state())

    @browsing
    def test_can_be_deactivated(self, browser):
        committee = create(Builder('committee').titled(u'My Committee'))

        browser.login().open(committee)
        browser.find('Deactivate').click()

        self.assertEqual(Committee.STATE_INACTIVE,
                         committee.load_model().get_state())
        self.assertEqual(['Committee deactivated successfully'],
                         info_messages())

    @browsing
    def test_deactivating_is_not_possible_when_pending_meetings_exists(self, browser):
        committee = create(Builder('committee').titled(u'My Committee'))
        create(Builder('meeting').having(committee=committee))

        browser.login().open(committee)
        browser.find('Deactivate').click()

        self.assertEqual(['Not all meetings are closed.'], error_messages())
        self.assertEqual(Committee.STATE_ACTIVE,
                         committee.load_model().get_state())

    @browsing
    def test_when_unscheduled_proposals_exist(self, browser):
        repo = create(Builder('repository'))
        dossier = create(Builder('dossier').within(repo))
        committee = create(Builder('committee').titled(u'My Committee'))
        proposal = create(Builder('proposal')
                          .within(dossier)
                          .having(committee=committee.load_model()))
        create(Builder('submitted_proposal').submitting(proposal))

        browser.login().open(committee)
        browser.find('Deactivate').click()

        self.assertEqual(
            ['There are unscheduled proposals submitted to this committee.'],
            error_messages())
        self.assertEqual(Committee.STATE_ACTIVE,
                         committee.load_model().get_state())

    @browsing
    def test_deactivated_comittee_can_be_reactivated(self, browser):
        committee = create(Builder('committee')
                           .titled(u'My Committee'))

        committee.load_model().deactivate()
        transaction.commit()

        browser.login().open(committee)
        browser.find('Activate').click()

        self.assertEqual(Committee.STATE_ACTIVE,
                         committee.load_model().get_state())
        self.assertEqual(['Committee reactivated successfully'],
                         info_messages())

    @browsing
    def test_add_meeting_is_not_available_on_inactive_committee(self, browser):
        committee = create(Builder('committee')
                           .titled(u'My Committee'))

        committee.load_model().deactivate()
        transaction.commit()

        browser.login().open(committee)
        self.assertEqual(
            [],
            browser.css('#plone-contentmenu-factories #add-meeting'))

    @browsing
    def test_add_membership_is_not_available_on_inactive_committee(self, browser):
        committee = create(Builder('committee')
                           .titled(u'My Committee'))

        committee.load_model().deactivate()
        transaction.commit()

        browser.login().open(committee)
        self.assertEqual(
            [],
            browser.css('#plone-contentmenu-factories #add-membership'))

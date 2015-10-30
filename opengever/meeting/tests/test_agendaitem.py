from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.browser.meetings.agendaitem import DeleteAgendaItem
from opengever.meeting.browser.meetings.agendaitem import ScheduleSubmittedProposal
from opengever.meeting.browser.meetings.agendaitem import ScheduleText
from opengever.meeting.browser.meetings.agendaitem import UpdateAgendaItemOrder
from opengever.meeting.model import Meeting
from opengever.meeting.model import Proposal
from opengever.meeting.model.agendaitem import AgendaItem
from opengever.meeting.wrapper import MeetingWrapper
from opengever.testing import FunctionalTestCase
from zExceptions import NotFound
from zExceptions import Unauthorized
import json
import transaction


class TestAgendaItem(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestAgendaItem, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.repository_root, self.repository_folder = create(
            Builder('repository_tree'))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repository_folder))
        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee.load_model(),
                                      start=datetime(2013, 1, 1),
                                      location='There',)
                              .link_with(self.meeting_dossier))

        self.meeting_wrapper = MeetingWrapper.wrap(self.committee, self.meeting)

    def setup_proposal(self):
        root, folder = create(Builder('repository_tree'))
        dossier = create(Builder('dossier').within(folder))
        proposal = create(Builder('proposal')
                          .within(dossier)
                          .having(committee=self.committee.load_model())
                          .as_submitted())

        return proposal

    def setup_proposal_agenda_item(self, browser):
        proposal = self.setup_proposal()
        proposal_model = proposal.load_model()

        browser.login().open(self.meeting.get_url())

        form = browser.css('#schedule_proposal').first
        form.fill({'proposal_id': str(proposal_model.proposal_id)}).submit()
        return proposal.load_model().agenda_item

    @browsing
    def test_free_text_agend_item_can_be_added(self, browser):
        browser.login().open(self.meeting.get_url())

        form = browser.css('#schedule_text').first
        form.fill({'title': 'My Agenda Item'})
        browser.css('#submit-schedule-text').first.click()

        meeting = Meeting.query.get(self.meeting.meeting_id)
        self.assertEqual(1, len(meeting.agenda_items))
        agenda_item = meeting.agenda_items[0]
        self.assertEqual('My Agenda Item', agenda_item.title)
        self.assertIsNone(agenda_item.proposal)
        self.assertFalse(agenda_item.is_paragraph)

    @browsing
    def test_paragraph_agenda_item_can_be_added(self, browser):
        browser.login().open(self.meeting.get_url())

        form = browser.css('#schedule_text').first
        form.fill({'title': 'My Paragraph'})
        browser.css('#submit-schedule-paragraph').first.click()

        meeting = Meeting.query.get(self.meeting.meeting_id)
        self.assertEqual(1, len(meeting.agenda_items))
        agenda_item = meeting.agenda_items[0]
        self.assertEqual('My Paragraph', agenda_item.title)
        self.assertIsNone(agenda_item.proposal)
        self.assertTrue(agenda_item.is_paragraph)

    @browsing
    def test_text_and_paragraph_agenda_item_disabled_for_closed_meetings(self, browser):
        self.meeting.execute_transition('pending-held')
        self.meeting.execute_transition('held-closed')
        transaction.commit()
        url = ScheduleText.url_for(self.committee, self.meeting)
        with self.assertRaises(Unauthorized):
            browser.login().open(url, data=dict(title='foo'))

    @browsing
    def test_proposal_agenda_item_can_be_added_to_meeting(self, browser):
        proposal = self.setup_proposal()
        proposal_model = proposal.load_model()

        browser.login().open(self.meeting.get_url())

        form = browser.css('#schedule_proposal').first
        form.fill({'proposal_id': str(proposal_model.proposal_id)}).submit()

        # refresh model instances
        meeting = Meeting.query.get(self.meeting.meeting_id)
        proposal_model = Proposal.query.get(proposal_model.proposal_id)

        self.assertEqual(1, len(meeting.agenda_items))
        agenda_item = meeting.agenda_items[0]
        self.assertIsNotNone(agenda_item.proposal)
        self.assertEqual(proposal_model, agenda_item.proposal)
        self.assertFalse(agenda_item.is_paragraph)

    @browsing
    def test_proposal_agenda_item_disabled_for_closed_meetings(self, browser):
        self.meeting.execute_transition('pending-held')
        self.meeting.execute_transition('held-closed')
        proposal = self.setup_proposal()
        proposal_model = proposal.load_model()
        transaction.commit()

        url = ScheduleSubmittedProposal.url_for(self.committee, self.meeting)
        with self.assertRaises(Unauthorized):
            browser.login().open(
                url, data=dict(proposal_id=proposal_model.proposal_id))

    @browsing
    def test_agenda_item_can_be_deleted(self, browser):
        create(Builder('agenda_item').having(meeting=self.meeting))
        self.assertEqual(1, len(self.meeting.agenda_items))

        browser.login().open(self.meeting.get_url())
        browser.css('.delete_agenda_item').first.click()

        # refresh model instances
        meeting = Meeting.query.get(self.meeting.meeting_id)
        self.assertEqual(0, len(meeting.agenda_items))

    @browsing
    def test_agenda_item_deletion_disabled_for_closed_meetings(self, browser):
        agenda_item = create(Builder('agenda_item').having(
            meeting=self.meeting))
        self.meeting.execute_transition('pending-held')
        self.meeting.execute_transition('held-closed')
        transaction.commit()

        url = DeleteAgendaItem.url_for(
            self.committee, self.meeting, agenda_item)
        with self.assertRaises(Unauthorized):
            browser.login().open(url)

    def test_update_agenda_item_order(self):
        item1 = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting, sort_order=1))
        item2 = create(Builder('agenda_item').having(
            title=u'bar', meeting=self.meeting, sort_order=2))

        self.assertEqual(1, item1.sort_order)
        self.assertEqual(2, item2.sort_order)

        view = UpdateAgendaItemOrder(
            MeetingWrapper.wrap(self.committee, self.meeting), self.request)
        view.update_sortorder({"sortOrder": [2, 1]})

        self.assertEqual(2, item1.sort_order)
        self.assertEqual(1, item2.sort_order)

    @browsing
    def test_wrong_params_raises_exception(self, browser):
        self.assertEqual(browser.login().open(
            MeetingWrapper.wrap(self.committee, self.meeting), view='update_agenda_item').json,
            {'messages': [{'messageClass': 'error',
                           'messageTitle': 'Error',
                           'message': 'Agenda Item title must not be empty.'}],
             'proceed': False})

    @browsing
    def test_not_found_item_raises_exception(self, browser):
        with self.assertRaises(NotFound):
            browser.login().open(MeetingWrapper.wrap(self.committee, self.meeting),
                                 view='update_agenda_item',
                                 data={'title': 'bar',
                                       'agenda_item_id': 23})

    @browsing
    def test_update_agenda_item(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        browser.login().open(MeetingWrapper.wrap(self.committee, self.meeting),
                             view='update_agenda_item',
                             data={'title': 'bar',
                                   'agenda_item_id': item.agenda_item_id})

        agenda_item = AgendaItem.get(item.agenda_item_id)
        self.assertEqual(agenda_item.title, 'bar')

    @browsing
    def test_update_proposal_agenda_item(self, browser):
        agenda_item = self.setup_proposal_agenda_item(browser)
        browser.login().open(MeetingWrapper.wrap(self.committee, self.meeting),
                             view='update_agenda_item',
                             data={'title': 'bar',
                                   'agenda_item_id': agenda_item.agenda_item_id})

        agenda_item = AgendaItem.get(agenda_item.agenda_item_id)
        self.assertEqual(agenda_item.get_title(), 'bar')


class TestAgendaItemEdit(TestAgendaItem):

    @browsing
    def test_update_agenda_item(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/edit'.format(item.agenda_item_id),
            data={'title': 'bar'})

        self.assertEqual(AgendaItem.get(item.agenda_item_id).title, 'bar')
        self.assertEquals([{u'message': u'Agenda Item updated.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))
        self.assertEquals(True, browser.json.get('proceed'))

    @browsing
    def test_when_title_is_missing_returns_json_error(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/edit'.format(item.agenda_item_id))

        self.assertEquals([{u'message': u'Agenda Item title must not be empty.',
                            u'messageClass': u'error',
                            u'messageTitle': u'Error'}],
                          browser.json.get('messages'))
        self.assertEquals(False, browser.json.get('proceed'))

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        with self.assertRaises(NotFound):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/12345/edit')

    @browsing
    def test_update_agenda_item_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(
                self.meeting_wrapper,
                view='agenda_items/{}/edit'.format(item.agenda_item_id),
                data={'title': 'bar'})


class TestAgendaItemDelete(TestAgendaItem):

    @browsing
    def test_delete_agenda_item(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        browser.login().open(
            self.meeting_wrapper,
            view='agenda_items/{}/delete'.format(item.agenda_item_id))

        self.assertEquals(0, AgendaItem.query.count())
        self.assertEquals([{u'message': u'Successfully deleted',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_raises_not_found_for_invalid_agenda_item_id(self, browser):
        with self.assertRaises(NotFound):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/12345/delete')

    @browsing
    def test_update_agenda_item_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        item = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting))

        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(
                self.meeting_wrapper,
                view='agenda_items/{}/delete'.format(item.agenda_item_id))


class TestAgendaItemUpdateOrder(TestAgendaItem):

    @browsing
    def test_update_agenda_item_order(self, browser):
        item1 = create(Builder('agenda_item').having(
            title=u'foo', meeting=self.meeting, sort_order=1))
        item2 = create(Builder('agenda_item').having(
            title=u'bar', meeting=self.meeting, sort_order=2))
        item3 = create(Builder('agenda_item').having(
            title=u'bar', meeting=self.meeting, sort_order=3))

        self.assertEqual(1, item1.sort_order)
        self.assertEqual(2, item2.sort_order)
        self.assertEqual(3, item3.sort_order)

        browser.login().open(self.meeting_wrapper,
                             view='agenda_items/update_order',
                             data={"sortOrder": json.dumps([1, 3, 2])})

        self.assertEqual(1, AgendaItem.get(1).sort_order)
        self.assertEqual(3, AgendaItem.get(2).sort_order)
        self.assertEqual(2, AgendaItem.get(3).sort_order)

        self.assertEquals([{u'message': u'Agenda Item order updated.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/update_order')


class TestScheduleParagraph(TestAgendaItem):

    @browsing
    def test_schedule_paragraph(self, browser):
        browser.login().open(self.meeting_wrapper,
                             view='agenda_items/schedule_paragraph',
                             data={'title': 'Abschnitt A'})

        agenda_items =  Meeting.get(self.meeting.meeting_id).agenda_items

        self.assertEquals(1, len(agenda_items))
        self.assertEqual(u'Abschnitt A', agenda_items[0].title)
        self.assertTrue(agenda_items[0].is_paragraph)

    @browsing
    def test_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/schedule_paragraph')

class TestScheduleText(TestAgendaItem):

    @browsing
    def test_schedule_text(self, browser):
        browser.login().open(self.meeting_wrapper,
                             view='agenda_items/schedule_text',
                             data={'title': u'Baugesuch Herr Maier'})

        agenda_items =  Meeting.get(self.meeting.meeting_id).agenda_items

        self.assertEquals(1, len(agenda_items))
        self.assertEqual(u'Baugesuch Herr Maier', agenda_items[0].title)
        self.assertFalse(agenda_items[0].is_paragraph)

    @browsing
    def test_raise_unauthorized_when_meeting_is_not_editable(self, browser):
        self.meeting.workflow_state = 'closed'

        with self.assertRaises(Unauthorized):
            browser.login().open(self.meeting_wrapper,
                                 view='agenda_items/schedule_paragraph')

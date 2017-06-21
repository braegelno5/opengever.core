from datetime import date
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages import z3cform
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase


class TestCommitteeType(IntegrationTestCase):
    features = ('meeting',)

    def test_committe_oguid_matches_model_oguid(self):
        self.login(self.administrator)
        model = self.committee.load_model()
        self.assertIsNotNone(model)
        self.assertEquals(Oguid.for_object(self.committee), model.oguid)

    @browsing
    def test_administrator_can_edit_committee(self, browser):
        self.login(self.administrator)
        browser.login(self.administrator).open(self.committee)
        browser.exception_bubbling = True
        browser.click_on('Edit')
        browser.fill({'Title': u'Ge\xe4nderter Gremiumtitel'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals('Ge\xc3\xa4nderter Gremiumtitel', self.committee.Title())

    def test_get_toc_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.committee_container.toc_template = None
        self.committee.toc_template = self.make_relation(self.sablon_template)
        self.assertEquals(self.sablon_template, self.committee.get_toc_template())

    def test_get_toc_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.committee_container.toc_template = self.make_relation(
            self.sablon_template)
        self.committee.toc_template = None
        self.assertEquals(self.sablon_template, self.committee.get_toc_template())

    @browsing
    def test_committee_repository_is_validated(self, browser):
        self.login(self.administrator)
        browser.login(self.administrator).open(self.committee_container)
        factoriesmenu.add('Committee')
        browser.fill({
            'Title': u'A c\xf6mmittee',
            'Linked repository folder': self.branch_repository,
            'Group': 'vip_group',
        }).find('Continue').click()
        self.assertIn(
            'You cannot add dossiers in the selected repository '
            'folder. Either you do not have the privileges or '
            'the repository folder contains another repository '
            'folder.',
            z3cform.erroneous_fields(browser.forms['form'])['fuhrung'])

    @browsing
    def test_committee_can_be_created_in_browser(self, browser):
        self.login(self.administrator)
        browser.login(self.administrator).open(self.committee_container)
        factoriesmenu.add('Committee')

        browser.fill({
            'Title': u'A c\xf6mmittee',
            'Protocol template': self.sablon_template,
            'Excerpt template': self.sablon_template,
            'Table of contents template': self.sablon_template,
            'Linked repository folder': self.leaf_repository,
            'Group': 'vip_group',
        }).find('Continue').click()
        statusmessages.assert_no_error_messages()
        self.assertEquals('add-initial-period', plone.view())

        browser.fill({
            'Title': u'Initial',
            'Start date': '01.01.2012',
            'End date': '31.12.2012',
        }).save()
        statusmessages.assert_message('Item created')

        committee = browser.context
        self.assertRegexpMatches(committee.getId(), '^committee-\d$')
        self.assertEqual(
            ('CommitteeGroupMember',),
            dict(committee.get_local_roles()).get('vip_group'))
        self.assertEqual(self.leaf_repository,
                         committee.get_repository_folder())
        self.assertEqual(self.sablon_template, committee.get_protocol_template())
        self.assertEqual(self.sablon_template, committee.get_excerpt_template())

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(committee), model.oguid)
        self.assertEqual(u'A c\xf6mmittee', model.title)

        self.assertEqual(1, len(model.periods))
        period = model.periods[0]
        self.assertEqual('active', period.workflow_state)
        self.assertEqual(u'Initial', period.title)
        self.assertEqual(date(2012, 1, 1), period.date_from)
        self.assertEqual(date(2012, 12, 31), period.date_to)

    @browsing
    def test_committee_can_be_edited_in_browser(self, browser):
        self.login(self.administrator)
        browser.login(self.administrator)

        self.assertEqual(
            {'committee_rpk_group': ('CommitteeGroupMember',),
             'nicole.kohler': ('Owner',)},
            dict(self.committee.get_local_roles()))

        browser.login(self.administrator).visit(self.committee, view='edit')
        form = browser.css('#content-core form').first
        self.assertEqual(u'Rechnungspr\xfcfungskommission',
                         form.find_field('Title').value)

        browser.fill({'Title': u'A c\xf6mmittee',
                      'Group': u'vip_group'}).save()
        statusmessages.assert_message('Changes saved')

        self.assertEqual(
            {'vip_group': ('CommitteeGroupMember',),
             'nicole.kohler': ('Owner',)},
            dict(self.committee.get_local_roles()))

        model = self.committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(u'A c\xf6mmittee', model.title)

    @browsing
    def test_committee_group_is_not_editable_for_users_with_missing_permission(
            self, browser):
        self.login(self.committee_member)
        browser.login(self.committee_member).open(self.committee, view='edit')
        with self.assertRaises(FormFieldNotFound):
            browser.fill({'Group': 'something'})

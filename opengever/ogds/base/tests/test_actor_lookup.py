from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import ogds_service
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestActorLookup(FunctionalTestCase):

    def setUp(self):
        super(TestActorLookup, self).setUp()
        self.grant('Reader', 'Contributor')

    def test_null_actor(self):
        actor = Actor.lookup('not-existing')

        self.assertEqual('not-existing', actor.get_label())
        self.assertIsNone(actor.get_profile_url())
        self.assertEqual('not-existing', actor.get_link())

    def test_inbox_actor_lookup(self):
        create(Builder('org_unit')
               .id('foobar')
               .having(title='Huhu',
                       admin_unit=self.admin_unit)
               .with_default_groups())
        actor = Actor.lookup('inbox:foobar')

        self.assertEqual('Inbox: Huhu', actor.get_label())
        self.assertIsNone(actor.get_profile_url())
        self.assertEqual('Inbox: Huhu', actor.get_link())
        self.assertEqual(u'foobar_inbox_users', actor.permission_identifier)

    def test_contact_actor_lookup(self):
        contact = create(Builder('contact')
                         .having(firstname=u'Hanspeter',
                                 lastname=u'Blahbla',
                                 email='h@example.com')
                         .in_state('published'))
        actor = Actor.lookup('contact:{}'.format(contact.id))
        self.assertEqual('Blahbla Hanspeter (h@example.com)',
                         actor.get_label())
        self.assertEqual(contact.absolute_url(), actor.get_profile_url())

        link = actor.get_link()
        self.assertIn(actor.get_label(), link)
        self.assertIn(actor.get_profile_url(), link)

    def test_user_actor_ogds_user(self):
        create(Builder('fixture'))
        create(Builder('ogds_user')
               .id('hugo.boss')
               .having(firstname='H\xc3\xbcgo'.decode('utf-8'),
                       lastname='Boss'))

        actor = Actor.lookup('hugo.boss')

        self.assertEqual(u'Boss H\xfcgo (hugo.boss)', actor.get_label())
        self.assertEqual('hugo.boss', actor.permission_identifier)
        self.assertTrue(
            actor.get_profile_url().endswith('@@user-details/hugo.boss'))

        self.assertEqual(
            u'<a href="http://nohost/plone/@@user-details/hugo.boss">Boss H\xfcgo (hugo.boss)</a>',
            actor.get_link())

        self.assertEqual(
            u'<a href="http://nohost/plone/@@user-details/hugo.boss" class="contenttype-opengever-actor">Boss H\xfcgo (hugo.boss)</a>',
            actor.get_link(with_icon=True))

    def test_get_link_returns_safe_html(self):
        contact = create(Builder('contact')
                         .having(firstname=u"Foo <b onmouseover=alert('Foo!')>click me!</b>",
                                 lastname=u'Blahbla',
                                 email='h@example.com')
                         .in_state('published'))
        actor = Actor.lookup('contact:{}'.format(contact.id))

        self.assertEquals(
            u'<a href="http://nohost/plone/blahbla-foo-b-onmouseover-alert-foo-click-me-b">'
            'Blahbla Foo &lt;b onmouseover=alert(&apos;Foo!&apos;)&gt;click me!&lt;/b&gt; (h@example.com)</a>',
            actor.get_link())


class TestActorCorresponding(FunctionalTestCase):

    def setUp(self):
        super(TestActorCorresponding, self).setUp()
        self.hugo = create(Builder('ogds_user')
                           .id('hugo.boss')
                           .having(firstname='H\xc3\xbcgo'.decode('utf-8'),
                                   lastname='Boss'))

    def test_user_corresponds_to_current_user(self):
        actor = Actor.lookup(TEST_USER_ID)

        self.assertTrue(actor.corresponds_to(self.user))
        self.assertFalse(actor.corresponds_to(self.hugo))

    def test_inbox_corresponds_to_all_inbox_assigned_users(self):
        actor = Actor.lookup('inbox:client1')

        self.assertTrue(actor.corresponds_to(self.user))
        self.assertFalse(actor.corresponds_to(self.hugo))


class TestActorRepresentatives(FunctionalTestCase):

    def setUp(self):
        super(TestActorRepresentatives, self).setUp()
        group = ogds_service().fetch_group(self.org_unit.inbox_group_id)
        self.hugo = create(Builder('ogds_user').id('hugo.boss').in_group(group))
        self.peter = create(Builder('ogds_user').id('peter'))
        self.james = create(Builder('ogds_user').id('james').in_group(group))

    def test_user_is_the_only_representatives_of_a_user(self):
        self.assertEquals([self.user],
                          Actor.lookup(TEST_USER_ID).representatives())
        self.assertEquals([self.peter],
                          Actor.lookup('peter').representatives())

    def test_all_users_of_the_inbox_group_are_inbox_representatives(self):
        actor = Actor.lookup('inbox:client1')
        self.assertItemsEqual([self.user, self.hugo, self.james],
                               actor.representatives())

    def test_contact_has_no_representatives(self):
        contact = create(Builder('contact')
                         .having(firstname=u'Paul')
                         .in_state('published'))

        actor = Actor.lookup('contact:{}'.format(contact.id))
        self.assertItemsEqual([], actor.representatives())

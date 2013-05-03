from ftw.tabbedview.interfaces import ITabbedView
from opengever.core.testing import OPENGEVER_FIXTURE
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.setuphandlers import _create_example_user
from opengever.ogds.base.utils import create_session
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TaskFunctionalLayer(PloneSandboxLayer):
    """Layer for integration tests."""

    defaultBases = (OPENGEVER_FIXTURE, )

    def setUpPloneSite(self, portal):
        session = create_session()

        # configure client ID
        registry = getUtility(IRegistry, context=portal)
        proxy = registry.forInterface(IClientConfiguration)
        proxy.client_id = u'plone'

        tab_reg = registry.forInterface(ITabbedView)
        tab_reg.batch_size = 5

        _create_example_client(session, 'plone',
                              {'title': 'plone',
                              'ip_address': '127.0.0.1',
                              'site_url': 'http://nohost/plone',
                              'public_url': 'http://nohost/plone',
                              'group': 'og_mandant1_users',
                              'inbox_group': 'og_mandant1_inbox'})

        _create_example_client(session, 'client2',
                            {'title': 'client2',
                            'ip_address': '127.0.0.1',
                            'site_url': 'http://nohost/plone',
                            'public_url': 'http://nohost/plone',
                            'group': 'og_mandant2_users',
                            'inbox_group': 'og_mandant2_inbox'})

        _create_example_user(session, portal, TEST_USER_ID, {
            'firstname': 'Test',
            'lastname': 'User',
            'email': 'test.user@local.ch',
            'email2': 'test_user@private.ch'},
            ('og_mandant1_users', 'og_mandant1_inbox', 'og_mandant2_users'))

        _create_example_user(session, portal, 'testuser2', {
            'firstname': 'Test',
            'lastname': 'User 2',
            'email': 'test2.user@local.ch',
            'email2': 'test_user@private.ch'},
            ('og_mandant2_users', 'og_mandant2_inbox',))

        setRoles(portal, TEST_USER_ID, ['Manager'])

    def tearDown(self):
        super(TaskFunctionalLayer, self).tearDown()
        truncate_sql_tables()


OPENGEVER_TASK_FIXTURE = TaskFunctionalLayer()
OPENGEVER_TASK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENGEVER_TASK_FIXTURE, ),
    name="OpengeverTask:Integration")
OPENGEVER_TASK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_TASK_FIXTURE, ),
    name="OpengeverTask:Functional")
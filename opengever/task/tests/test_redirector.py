from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestTaskRedirector(FunctionalTestCase):

    def setUp(self):
        super(TestTaskRedirector, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_redirects_to_dossiers_task_tab_when_creating_a_maintask(self, browser):
        browser.login().open(self.dossier)
        factoriesmenu.add('Task')
        browser.fill({'Title': 'Main task',
                      'Task Type': 'direct-execution'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('client1:' + TEST_USER_ID)

        browser.click_on('Save')

        self.assertEquals('{}#tasks'.format(self.dossier.absolute_url()),
                          browser.url)

    @browsing
    def test_redirects_to_maintask_overview_tab_when_creating_a_subtask(self, browser):
        task = create(Builder('task')
                      .within(self.dossier)
                      .having(title='Subtask',
                              task_type='approval',
                              responsible=TEST_USER_ID,
                              issuer=TEST_USER_ID)
                      .in_state('task-state-in-progress'))

        browser.login().open(task)
        factoriesmenu.add('Subtask')
        browser.fill({'Title': 'Subtask',
                      'Task Type': 'direct-execution'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('client1:' + TEST_USER_ID)

        browser.click_on('Save')

        self.assertEquals('{}#overview'.format(task.absolute_url()),
                          browser.url)

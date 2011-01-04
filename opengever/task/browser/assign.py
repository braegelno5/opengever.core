from five import grok
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.task import _
from opengever.task.task import ITask
from plone.directives import form
from plone.z3cform import layout
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import INPUT_MODE
from zope import schema
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class IAssignSchema(form.Schema):
    """ Form schema interface for assign wizard which makes it possible to
    a task to another person.
    """

    responsible_client = schema.Choice(
        title=_(u'label_resonsible_client',
                default=u'Responsible Client'),
        description=_(u'help_responsible_client',
                      default=u''),
        vocabulary='opengever.ogds.base.ClientsVocabulary',
        required=True)

    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description =_(u"help_responsible", default=""),
        vocabulary=u'opengever.ogds.base.UsersAndInboxesVocabulary',
        required = True,
        )


class AssignTaskForm(Form):
    """Form for assigning task.
    """

    fields = Fields(IAssignSchema)
    fields['responsible'].widgetFactory[INPUT_MODE] = \
        AutocompleteFieldWidget
    ignoreContext = True

    label = _(u'title_assign_task', u'Assign task')

    @buttonAndHandler(_(u'button_assign', default=u'Assign'))
    def handle_assign(self, action):
        data, errors = self.extractData()
        if not errors:
            self.context.responsible_client = data['responsible_client']
            self.context.responsible = data['responsible']
            notify(ObjectModifiedEvent(self.context))
            return self.request.RESPONSE.redirect('.')

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')


class AssignTaskView(layout.FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('assign-task')
    grok.require('cmf.ModifyPortalContent')

    form = AssignTaskForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.CodeView.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__

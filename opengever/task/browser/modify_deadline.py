from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.task import _
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.task import ITask
from opengever.task.util import getTransitionVocab
from plone.directives import form
from plone.z3cform import layout
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import WidgetActionExecutionError
from zope import schema
from zope.interface import Invalid


class IModifyDeadlineSchema(form.Schema):

    # hidden
    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        source=getTransitionVocab,
        required=True,
        )

    new_deadline = schema.Date(
        title=_(u"label_new_deadline", default=u"New Deadline"),
        required=True,
        )

    text = schema.Text(
        title=_('label_response', default="Response"),
        required=False,
        )


class ModifyDeadlineForm(Form):
    """Form wich allows to modify the deadline of a task."""

    fields = Fields(IModifyDeadlineSchema)
    fields['new_deadline'].widgetFactory = DatePickerFieldWidget
    ignoreContext = True
    allow_prefill_from_GET_request = True  # XXX

    label = _(u'title_modify_deadline', u'Modify deadline')

    def updateActions(self):
        super(ModifyDeadlineForm, self).updateActions()
        self.actions["save"].addClass("context")

    @buttonAndHandler(_(u'button_save', default=u'Save'), name='save')
    def handle_save(self, action):
        data, errors = self.extractData()
        if not errors:

            if data.get('new_deadline') == self.context.deadline:
                raise WidgetActionExecutionError(
                    'new_deadline', Invalid(
                        _('same_deadline_error',
                          default=u'The given deadline, is the current one.')))

            IDeadlineModifier(self.context).modify_deadline(
                data.get('new_deadline'),
                data.get('text'),
                data.get('transition'))

            msg = _(u'msg_deadline_change_successfull',
                    default=u'Deadline successfully changed.')
            IStatusMessage(self.request).addStatusMessage(msg, type='info')

            return self.request.RESPONSE.redirect(self.context.absolute_url())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def updateWidgets(self):
        super(ModifyDeadlineForm, self).updateWidgets()
        self.widgets['transition'].mode = HIDDEN_MODE


class ModifyDeadlineFormView(layout.FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('modify_deadline')
    grok.require('zope2.View')

    form = ModifyDeadlineForm

    @classmethod
    def url_for(cls, context, transition):
        return '{}/@@modify_deadline?form.widgets.transition={}'.format(
            context.absolute_url(), transition)

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__

from opengever.officeconnector import _
from zope import schema
from zope.interface import Interface


class IOfficeconnectorSettings(Interface):

    attach_to_outlook_enabled = schema.Bool(
        title=_(u'label_enable_officeconnector_attach_to_outlook',
                default=u'OfficeConnector Outlook support'),
        description=_(u'label_enable_officeconnector_description',
                      default=(u'Enable attach to Outlook with the new style '
                               u'OfficeConnector URLs')),
        default=False)

    direct_checkout_and_edit_enabled = schema.Bool(
        title=_(u'label_enable_officeconnector_direct_checkout_and_edit',
                default=u'OfficeConnector direct checkout suppport'),
        description=_(u'label_enable_officeconnector_description',
                      default=(u'Enable direct checkout and edit with the '
                               u'new style OfficeConnector URLs')),
        default=False)

from opengever.officeconnector.helpers import is_officeconnector_attach_enabled
from opengever.officeconnector.helpers import is_officeconnector_checkout_enabled # noqa
from Products.Five import BrowserView


class OfficeconnectorAttachEnabledView(BrowserView):

    def __call__(self):
        return is_officeconnector_attach_enabled()


class OfficeconnectorCheckoutEnabledView(BrowserView):

    def __call__(self):
        return is_officeconnector_checkout_enabled()

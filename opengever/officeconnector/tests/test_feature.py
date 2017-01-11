from opengever.officeconnector.helpers import is_officeconnector_attach_enabled
from opengever.officeconnector.helpers import is_officeconnector_checkout_enabled # noqa
from opengever.officeconnector.interfaces import IOfficeconnectorSettings
from opengever.testing import FunctionalTestCase
from plone import api


class TestIsOfficeconnectorFeatureEnabled(FunctionalTestCase):

    def test_if_registry_entries_are_false_per_default(self):
        self.assertFalse(is_officeconnector_attach_enabled())
        self.assertFalse(is_officeconnector_checkout_enabled())

    def test_if_registry_entries_are_true(self):
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeconnectorSettings)
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeconnectorSettings)

        self.assertTrue(is_officeconnector_attach_enabled())
        self.assertTrue(is_officeconnector_checkout_enabled())

    def test_if_registry_entries_are_false(self):
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeconnectorSettings)
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            False,
            interface=IOfficeconnectorSettings)

        self.assertFalse(is_officeconnector_attach_enabled())
        self.assertFalse(is_officeconnector_checkout_enabled())


class TestIsOfficeconnectorFeatureEnabledView(FunctionalTestCase):

    def test_if_registry_entries_are_false_per_default(self):
        attach_feature_view = self.portal.restrictedTraverse(
            '@@is_officeconnector_attach_enabled')
        checkout_feature_view = self.portal.restrictedTraverse(
            '@@is_officeconnector_checkout_enabled')

        self.assertFalse(attach_feature_view())
        self.assertFalse(checkout_feature_view())

    def test_if_registry_entry_is_true(self):
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            True,
            interface=IOfficeconnectorSettings)
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeconnectorSettings)

        attach_feature_view = self.portal.restrictedTraverse(
            '@@is_officeconnector_attach_enabled')
        checkout_feature_view = self.portal.restrictedTraverse(
            '@@is_officeconnector_checkout_enabled')

        self.assertTrue(attach_feature_view())
        self.assertTrue(checkout_feature_view())

    def test_false_if_registry_entry_is_false(self):
        api.portal.set_registry_record(
            'attach_to_outlook_enabled',
            False,
            interface=IOfficeconnectorSettings)
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            False,
            interface=IOfficeconnectorSettings)

        attach_feature_view = self.portal.restrictedTraverse(
            '@@is_officeconnector_attach_enabled')
        checkout_feature_view = self.portal.restrictedTraverse(
            '@@is_officeconnector_checkout_enabled')

        self.assertFalse(attach_feature_view())
        self.assertFalse(checkout_feature_view())

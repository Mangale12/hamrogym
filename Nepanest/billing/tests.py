from django.contrib.auth import get_user_model
from django.test import TestCase

from Nepanest.assets.models import AssetVendor
from Nepanest.hr.models import Department
from core.models import Currency, Organization

from .forms import BillingProfileForm


class BillingProfileFormTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="billing-user",
            password="test-pass-123",
        )
        self.organization = Organization.objects.create(
            name="Hamro Gym",
            code="HAMRO",
        )
        self.currency = Currency.objects.create(
            code="NPR",
            name="Nepalese Rupee",
            symbol="Rs.",
            created_by=self.user,
        )
        self.vendor = AssetVendor.objects.create(
            name="Vendor One",
            code="V001",
        )
        self.department = Department.objects.create(
            name="Finance",
            code="FIN",
            organization=self.organization,
        )

    def test_form_requires_relation_for_selected_billing_type(self):
        form = BillingProfileForm(
            data={
                "name": "Missing Customer",
                "billing_type": "customer",
                "currency": self.currency.pk,
                "credit_limit": "0.00",
                "is_active": "on",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("customer", form.errors)

    def test_form_saves_vendor_relation_and_restores_selected_field(self):
        form = BillingProfileForm(
            data={
                "name": "Vendor Billing",
                "billing_type": "vendor",
                "vendor": self.vendor.pk,
                "currency": self.currency.pk,
                "credit_limit": "2500.00",
                "is_active": "on",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()

        self.assertEqual(instance.related_object, self.vendor)
        self.assertEqual(instance.content_type.model_class(), AssetVendor)
        self.assertEqual(instance.object_id, self.vendor.pk)

        edit_form = BillingProfileForm(instance=instance)
        self.assertEqual(edit_form.fields["vendor"].initial, self.vendor.pk)
        self.assertIsNone(edit_form.fields["customer"].initial)

    def test_form_saves_internal_relation(self):
        form = BillingProfileForm(
            data={
                "name": "Internal Billing",
                "billing_type": "internal",
                "department": self.department.pk,
                "currency": self.currency.pk,
                "credit_limit": "1000.00",
                "is_active": "on",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()

        self.assertEqual(instance.related_object, self.department)

from django import forms
from django.contrib.contenttypes.models import ContentType

from Nepanest.assets.models import AssetVendor
from Nepanest.hr.models import Department
from core.models import Organization

from ..models import BillingProfile


class BillingProfileForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Organization.objects.order_by("name"),
        required=False,
        label="Customer",
    )
    vendor = forms.ModelChoiceField(
        queryset=AssetVendor.objects.order_by("name"),
        required=False,
        label="Vendor",
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.order_by("name"),
        required=False,
        label="Department",
    )
    partner = forms.ModelChoiceField(
        queryset=Organization.objects.order_by("name"),
        required=False,
        label="Partner",
    )

    relation_fields = {
        "customer": ("customer", Organization),
        "vendor": ("vendor", AssetVendor),
        "internal": ("department", Department),
        "partner": ("partner", Organization),
    }

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        if not self.instance or not self.instance.pk or not self.instance.content_type_id:
            return

        field_name, expected_model = self.relation_fields.get(self.instance.billing_type, (None, None))
        related_object = self.instance.related_object
        if field_name and expected_model and isinstance(related_object, expected_model):
            self.fields[field_name].initial = related_object.pk

    def clean(self):
        cleaned_data = super().clean()
        billing_type = cleaned_data.get("billing_type")
        relation_config = self.relation_fields.get(billing_type)

        if not relation_config:
            self.add_error("billing_type", "Select a valid billing type.")
            return cleaned_data

        field_name, _model_class = relation_config
        related_object = cleaned_data.get(field_name)

        if not related_object:
            self.add_error(field_name, f"{self.fields[field_name].label} is required for this billing type.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        field_name, _model_class = self.relation_fields[self.cleaned_data["billing_type"]]
        related_object = self.cleaned_data[field_name]

        instance.content_type = ContentType.objects.get_for_model(
            related_object,
            for_concrete_model=False,
        )
        instance.object_id = related_object.pk

        if commit:
            instance.save()
            self.save_m2m()

        return instance

    class Meta:
        model = BillingProfile
        fields = [
            "name",
            "billing_type",
            "customer",
            "vendor",
            "department",
            "partner",
            "tax_number",
            "registration_number",
            "currency",
            "credit_limit",
            "is_active",
            "remarks",
        ]

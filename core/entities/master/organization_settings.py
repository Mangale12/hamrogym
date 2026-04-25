from django.core.cache import cache

from core.config import EntityConfig
from core.datatables.organization_settings import OrganizationSettingsDataTableView
from core.forms.organization_settings_form import OrganizationSettingsForm
from nepanest.foundation.organization import OrganizationSettings
from core.registry import register_entity


def clear_organization_settings_cache(request, obj):
    cache.delete("organization_settings")


register_entity(
    EntityConfig(
        name="organization_settings",
        url_path="organization-settings",
        verbose_name="Organization Settings",
        model=OrganizationSettings,
        form_class=OrganizationSettingsForm,
        datatable_view=OrganizationSettingsDataTableView,
        template_name="organization_settings/index.html",
        fields=[
            {
                "name": "name",
                "label": "Organization Name",
                "type": "text",
                "required": False,
                "col": 6,
                "placeholder": "HamroGym Pvt. Ltd.",
            },
            {
                "name": "registration_number",
                "label": "Registration Number",
                "type": "text",
                "required": False,
                "col": 6,
                "placeholder": "REG-001",
            },
            {
                "name": "pan_vat_number",
                "label": "PAN / VAT Number",
                "type": "text",
                "required": False,
                "col": 6,
                "placeholder": "123456789",
            },
            {
                "name": "phone",
                "label": "Phone",
                "type": "text",
                "required": False,
                "col": 6,
                "placeholder": "+977-1-0000000",
            },
            {
                "name": "email",
                "label": "Email",
                "type": "email",
                "required": False,
                "col": 6,
                "placeholder": "info@hamrogym.com",
            },
            {
                "name": "website",
                "label": "Website",
                "type": "url",
                "required": False,
                "col": 6,
                "placeholder": "https://hamrogym.com",
            },
            {
                "name": "contact_person",
                "label": "Contact Person",
                "type": "text",
                "required": False,
                "col": 6,
                "placeholder": "Admin Manager",
            },
            {
                "name": "calendar",
                "label": "Calendar",
                "type": "static_select",
                "required": False,
                "col": 6,
                "options": [("AD", "AD"), ("BS", "BS")],
            },
            {
                "name": "logo",
                "label": "Logo",
                "type": "file",
                "required": False,
                "col": 6,
                "accept": "image/*",
            },
            {
                "name": "address",
                "label": "Address",
                "type": "textarea",
                "required": False,
                "col": 12,
                "placeholder": "Organization address",
            },
        ],
        datatable_columns=[],
        reset_defaults={"calendar": "AD"},
        show_actions=False,
        show_create=False,
        show_view=False,
        singleton=True,
        post_save=clear_organization_settings_cache,
    )
)

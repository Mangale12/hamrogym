from core.config import EntityConfig
from core.registry import register_entity

from ..datatables.license_data_table import (
    LICENSE_COLUMNS,
    LICENSE_HISTORY_COLUMNS,
    LicenseDataTableView,
    LicenseRenewHistoryDataTableView,
)
from ..forms.license_form import LicenseForm, LicenseRenewHistoryForm
from ..models import License, LicenseRenewHistory


register_entity(
    EntityConfig(
        name="license",
        url_path="licenses",
        verbose_name="License",
        model=License,
        form_class=LicenseForm,
        datatable_view=LicenseDataTableView,
        fields=[
            {
                "name": "client",
                "label": "Client",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "client_select",
            },
            {
                "name": "plan",
                "label": "Plan",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": License.Plan.choices,
            },
            {"name": "issued_on", "label": "Issued On", "type": "date", "required": True, "col": 6},
            {"name": "expires_on", "label": "Expires On", "type": "date", "required": True, "col": 6},
            {"name": "max_users", "label": "Max Users", "type": "number", "required": True, "col": 6},
            {"name": "max_branches", "label": "Max Branches", "type": "number", "required": True, "col": 6},
            {"name": "grace_days", "label": "Grace Days", "type": "number", "required": True, "col": 6},
            {"name": "is_current", "label": "Is Current", "type": "checkbox", "required": False, "col": 6, "default": True},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LICENSE_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "plan": License.Plan.STARTER,
            "max_users": 5,
            "max_branches": 1,
            "grace_days": 7,
            "is_current": True,
        },
        select_search_fields=["client__business_name", "client__client_code", "plan"],
        select_label_func=lambda obj: f"{obj.client} - {obj.get_plan_display()} (expires {obj.expires_on})",
    )
)


register_entity(
    EntityConfig(
        name="license_renew_history",
        url_path="license-renew-history",
        verbose_name="License Renew History",
        model=LicenseRenewHistory,
        form_class=LicenseRenewHistoryForm,
        datatable_view=LicenseRenewHistoryDataTableView,
        fields=[
            {
                "name": "license",
                "label": "License",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "license_select",
            },
            {
                "name": "old_expiry",
                "label": "Old Expiry",
                "type": "date",
                "required": True,
                "col": 6,
            },
            {"name": "new_expiry", "label": "New Expiry", "type": "date", "required": True, "col": 6},
            {"name": "renewed_by", "label": "Renewed By", "type": "text", "required": True, "col": 6},
            {"name": "renewed_at", "label": "Renewed At", "type": "datetime", "required": True, "col": 6},
            {"name": "notes", "label": "Notes", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in LICENSE_HISTORY_COLUMNS
            if key != "id"
        ],
        select_search_fields=["license__client__business_name", "license__client__client_code", "renewed_by", "notes"],
        select_label_func=lambda obj: f"{obj.license} - {obj.old_expiry} -> {obj.new_expiry}",
    )
)

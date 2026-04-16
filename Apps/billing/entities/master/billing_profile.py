from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.billing_profile_data_table import BillingProfileDataTableView, BILLING_PROFILE_COLUMNS
from ...forms.billing_profile_form import BillingProfileForm
from ...models import BillingProfile


_datatable_columns = []
for key, _accessor in BILLING_PROFILE_COLUMNS:
    if key == "id":
        continue
    column = {"name": key, "title": key.replace("_", " ").title()}
    if key == "billing_type":
        column["title"] = "Billing Type"
    elif key == "related_object":
        column["title"] = "Linked To"
    elif key == "is_active":
        column["title"] = "Active"
    _datatable_columns.append(column)


register_entity(
    EntityConfig(
        name="billing_profile",
        url_path="billing-profiles",
        verbose_name="Billing Profile",
        model=BillingProfile,
        form_class=BillingProfileForm,
        datatable_view=BillingProfileDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {
                "name": "billing_type",
                "label": "Billing Type",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": BillingProfile.BILLING_TYPE_CHOICES,
            },
            {
                "name": "customer",
                "label": "Customer",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "organization_select",
            },
            {
                "name": "vendor",
                "label": "Vendor",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "asset_vendor_select",
            },
            {
                "name": "department",
                "label": "Department",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "department_select",
            },
            {
                "name": "partner",
                "label": "Partner",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "organization_select",
            },
            {"name": "tax_number", "label": "Tax Number", "type": "text", "required": False, "col": 6},
            {
                "name": "registration_number",
                "label": "Registration Number",
                "type": "text",
                "required": False,
                "col": 6,
            },
            {
                "name": "currency",
                "label": "Currency",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "currency_select",
            },
            {
                "name": "credit_limit",
                "label": "Credit Limit",
                "type": "number",
                "required": False,
                "col": 6,
                "min": 0,
                "step": "0.01",
            },
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=_datatable_columns,
        reset_defaults={"is_active": True, "credit_limit": 0},
    )
)

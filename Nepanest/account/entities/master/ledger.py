from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.ledger_data_table import LedgerDataTableView
from ...forms.ledger_form import LedgerForm
from ...models import ACCOUNT_TYPE_CHOICES, ChartOfAccount, Ledger


def _prepare_ledger_account(request, obj: ChartOfAccount):
    obj.is_ledger = True
    obj.allow_direct_posting = True


def _sync_ledger_profile(request, obj: ChartOfAccount):
    payload = getattr(obj, "_ledger_payload", {})
    Ledger.objects.update_or_create(
        chart_account=obj,
        defaults={
            "pan_no": payload.get("pan_no", ""),
            "vat_no": payload.get("vat_no", ""),
            "contact_person": payload.get("contact_person", ""),
            "mobile_no": payload.get("mobile_no", ""),
            "email": payload.get("email", ""),
            "address": payload.get("address", ""),
        },
    )


register_entity(
    EntityConfig(
        name="ledger_account",
        url_path="ledgers",
        verbose_name="Ledger",
        model=ChartOfAccount,
        form_class=LedgerForm,
        datatable_view=LedgerDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "col": 4, "url_name": "branch_select"},
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "col": 4, "url_name": "fiscal_year_select"},
            {
                "name": "parent",
                "label": "Parent Account",
                "type": "select",
                "col": 6,
                "url_name": "chart_of_account_parent_select",
                "attributes": {"data-tree-select": "true"},
            },
            {
                "name": "account_type",
                "label": "Account Type",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": ACCOUNT_TYPE_CHOICES,
            },
            {"name": "name", "label": "Ledger Name", "type": "text", "required": True, "col": 6},
            {
                "name": "code",
                "label": "Ledger Code",
                "type": "text",
                "required": False,
                "col": 3,
                "attributes": {"readonly": "readonly"},
            },
            {
                "name": "report_level",
                "label": "Report Level",
                "type": "number",
                "required": False,
                "col": 3,
                "attributes": {"readonly": "readonly"},
            },
            {
                "name": "sort_order",
                "label": "Sort Order",
                "type": "number",
                "required": False,
                "col": 3,
                "attributes": {"min": "0"},
            },
            {"name": "is_depreciation", "label": "Is Depreciation Ledger", "type": "checkbox", "col": 3},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "col": 3},
            {"name": "pan_no", "label": "PAN No", "type": "text", "col": 4},
            {"name": "vat_no", "label": "VAT No", "type": "text", "col": 4},
            {"name": "contact_person", "label": "Contact Person", "type": "text", "col": 4},
            {"name": "mobile_no", "label": "Mobile No", "type": "text", "col": 4},
            {"name": "email", "label": "Email", "type": "email", "col": 4},
            {"name": "address", "label": "Address", "type": "textarea", "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "col": 12},
        ],
        datatable_columns=[
            {"name": "code", "title": "Ledger Code"},
            {"name": "name", "title": "Ledger Name"},
            {"name": "parent", "title": "Parent Account"},
            {"name": "account_type", "title": "Account Type"},
            {"name": "pan_no", "title": "PAN No"},
            {"name": "vat_no", "title": "VAT No"},
            {"name": "contact_person", "title": "Contact Person"},
            {"name": "mobile_no", "title": "Mobile No"},
            {"name": "is_active", "title": "Active"},
        ],
        reset_defaults={
            "is_active": True,
            "sort_order": 0,
        },
        select_search_fields=["code", "name", "parent__name", "ledger_profile__pan_no", "ledger_profile__vat_no"],
        select_label_func=lambda obj: f"{obj.code or 'AUTO'} - {obj.full_path}",
        select_queryset_builder=lambda request=None, term="": ChartOfAccount.objects.filter(is_ledger=True),
        select_order_by="code",
        datatable_options={"order": [[1, "asc"]]},
        pre_save=_prepare_ledger_account,
        post_save=_sync_ledger_profile,
    )
)

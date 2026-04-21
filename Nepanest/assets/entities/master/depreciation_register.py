from django.core.exceptions import ValidationError

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.depreciation_register_data_table import (
    ASSET_DEPRECIATION_REGISTER_COLUMNS,
    AssetDepreciationRegisterDataTableView,
)
from ...forms.depreciation_register_form import AssetDepreciationRegisterForm
from ...models import AssetDepreciationRegister
from ...services import post_depreciation_entry


def _post_depreciation_register(request, register_entry: AssetDepreciationRegister):
    if register_entry.status == AssetDepreciationRegister.STATUS_POSTED:
        raise ValidationError("This depreciation register entry is already posted.")

    posted = post_depreciation_entry(register_entry, user=request.user)
    journal_label = posted.journal_entry.entry_no if posted.journal_entry_id else "journal entry"
    return {
        "message": f"Depreciation posted successfully with {journal_label}.",
    }


register_entity(
    EntityConfig(
        name="asset_depreciation_register",
        url_path="asset-depreciation-registers",
        verbose_name="Asset Depreciation Register",
        model=AssetDepreciationRegister,
        form_class=AssetDepreciationRegisterForm,
        datatable_view=AssetDepreciationRegisterDataTableView,
        template_name="assets/depreciation_register_index.html",
        fields=[
            {"name": "asset", "label": "Asset", "type": "select", "col": 4, "url_name": "asset_select"},
            {"name": "organization", "label": "Organization", "type": "select", "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "col": 4, "url_name": "branch_select"},
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "col": 4, "url_name": "fiscal_year_select"},
            {"name": "schedule_month", "label": "Schedule Month", "type": "date", "col": 4},
            {"name": "period_start", "label": "Period Start", "type": "date", "col": 4},
            {"name": "period_end", "label": "Period End", "type": "date", "col": 4},
            {"name": "method", "label": "Method", "type": "text", "col": 4},
            {"name": "life_month_index", "label": "Life Month Index", "type": "number", "col": 4},
            {"name": "useful_life_months", "label": "Useful Life Months", "type": "number", "col": 4},
            {"name": "purchase_cost", "label": "Purchase Cost", "type": "number", "col": 3},
            {"name": "salvage_value", "label": "Salvage Value", "type": "number", "col": 3},
            {"name": "depreciable_amount", "label": "Depreciable Amount", "type": "number", "col": 3},
            {"name": "depreciation_amount", "label": "Depreciation Amount", "type": "number", "col": 3},
            {"name": "opening_book_value", "label": "Opening Book Value", "type": "number", "col": 4},
            {"name": "closing_book_value", "label": "Closing Book Value", "type": "number", "col": 4},
            {"name": "status", "label": "Status", "type": "static_select", "col": 4, "options": AssetDepreciationRegister.STATUS_CHOICES},
            {"name": "fixed_asset_account", "label": "Fixed Asset Ledger", "type": "select", "col": 4, "url_name": "ledger_account_select"},
            {"name": "depreciation_expense_account", "label": "Depreciation Expense Ledger", "type": "select", "col": 4, "url_name": "ledger_account_select"},
            {"name": "accumulated_depreciation_account", "label": "Accumulated Depreciation Ledger", "type": "select", "col": 4, "url_name": "ledger_account_select"},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "col": 12},
        ],
        datatable_columns=[
            {
                "name": key,
                "title": {
                    "schedule_month": "Schedule Month",
                    "period_start": "Period Start",
                    "period_end": "Period End",
                    "depreciation_amount": "Depreciation",
                    "opening_book_value": "Opening BV",
                    "closing_book_value": "Closing BV",
                    "journal_entry": "Journal Entry",
                }.get(key, key.replace("_", " ").title()),
            }
            for key, _accessor in ASSET_DEPRECIATION_REGISTER_COLUMNS
            if key != "id"
        ],
        row_actions={
            "post_depreciation": _post_depreciation_register,
        },
        action_state_field="status",
        hide_edit_on_values=[
            AssetDepreciationRegister.STATUS_UNPOSTED,
            AssetDepreciationRegister.STATUS_POSTED,
        ],
        hide_delete_on_values=[AssetDepreciationRegister.STATUS_POSTED],
        action_buttons=[
            {
                "action_name": "post_depreciation",
                "title": "Post",
                "icon_class": "fas fa-check-circle",
                "class_name": "btn-outline-success",
                "confirm_text": "Post this depreciation entry to accounting journals?",
                "success_message": "Depreciation entry posted successfully.",
                "hide_on_values": [AssetDepreciationRegister.STATUS_POSTED],
            },
        ],
        select_search_fields=[
            "asset__name",
            "asset__code",
            "status",
            "journal_entry__entry_no",
        ],
        select_label_func=lambda obj: f"{obj.asset.name} - {obj.schedule_month:%Y-%m}",
        reset_defaults={"status": AssetDepreciationRegister.STATUS_UNPOSTED},
        show_create=False,
        show_view=False,
    )
)

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.voucher_type_data_table import VOUCHER_TYPE_COLUMNS, VoucherTypeDataTableView
from ...forms.voucher_type_form import VoucherTypeForm
from ...models import CATEGORY_CHOICES, NATURE_CHOICES, VoucherType


register_entity(
    EntityConfig(
        name="voucher_type",
        url_path="voucher-types",
        verbose_name="Voucher Type",
        model=VoucherType,
        form_class=VoucherTypeForm,
        datatable_view=VoucherTypeDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "col": 4, "url_name": "branch_select"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4},
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 4},
            {"name": "category", "label": "Category", "type": "static_select", "required": True, "col": 4, "options": CATEGORY_CHOICES},
            {"name": "nature", "label": "Nature", "type": "static_select", "required": True, "col": 4, "options": NATURE_CHOICES},
            {"name": "affects_cash", "label": "Affects Cash", "type": "checkbox", "col": 3},
            {"name": "affects_bank", "label": "Affects Bank", "type": "checkbox", "col": 3},
            {"name": "auto_numbering", "label": "Auto Numbering", "type": "checkbox", "col": 3},
            {"name": "requires_reference", "label": "Requires Reference", "type": "checkbox", "col": 3},
            {"name": "requires_approval", "label": "Requires Approval", "type": "checkbox", "col": 3},
            {"name": "allow_negative", "label": "Allow Negative", "type": "checkbox", "col": 3},
            {"name": "is_system_generated", "label": "System Generated", "type": "checkbox", "col": 3},
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "col": 3},
            {"name": "prefix", "label": "Prefix", "type": "text", "col": 3},
            {"name": "last_number", "label": "Last Number", "type": "number", "col": 3, "attributes": {"min": "0"}},
            {"name": "description", "label": "Description", "type": "textarea", "col": 12},
        ],
        datatable_columns=[
            {
                "name": key,
                "title": {
                    "affects_cash": "Cash",
                    "affects_bank": "Bank",
                    "auto_numbering": "Auto No",
                    "requires_reference": "Ref Required",
                    "requires_approval": "Approval",
                    "allow_negative": "Allow Negative",
                    "is_system_generated": "System",
                    "is_active": "Active",
                    "last_number": "Last No",
                }.get(key, key.replace("_", " ").title()),
            }
            for key, _accessor in VOUCHER_TYPE_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "category": "journal",
            "nature": "both",
            "auto_numbering": True,
            "prefix": "",
            "last_number": 0,
            "is_active": True,
        },
        select_search_fields=["code", "name", "category", "nature", "description"],
        select_label_func=lambda obj: f"{obj.code} - {obj.name}",
        select_order_by="name",
    )
)

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.credit_transaction_data_table import CreditTransactionDataTableView
from ...forms import CreditTransactionForm
from ...models import CreditTransaction


register_entity(
    EntityConfig(
        name="credit_transaction",
        url_path="credit-transactions",
        verbose_name="Credit Transaction",
        model=CreditTransaction,
        form_class=CreditTransactionForm,
        datatable_view=CreditTransactionDataTableView,
        fields=[
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": False, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "party", "label": "Party", "type": "select", "required": True, "col": 4, "url_name": "party_select"},
            {"name": "document_type", "label": "Document Type", "type": "static_select", "required": True, "col": 3, "options": CreditTransaction._meta.get_field("document_type").choices},
            {"name": "document_id", "label": "Document ID", "type": "text", "required": False, "col": 3},
            {"name": "transaction_date", "label": "Date", "type": "date", "required": True, "col": 3},
            {"name": "debit", "label": "Debit", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "credit", "label": "Credit", "type": "number", "required": False, "col": 3, "attributes": {"step": "0.01", "min": "0"}},
            {"name": "is_system_generated", "label": "System Generated", "type": "checkbox", "required": False, "col": 3, "default": True},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": "transaction_date", "title": "Date"},
            {"name": "party", "title": "Party"},
            {"name": "document_type", "title": "Document Type"},
            {"name": "document_id", "title": "Document ID", "render": "function(data){return data || '-';}"},
            {"name": "debit", "title": "Debit"},
            {"name": "credit", "title": "Credit"},
            {"name": "balance_after", "title": "Balance After"},
            {"name": "is_system_generated", "title": "System", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "created_at", "title": "Created At"},
        ],
        reset_defaults={
            "debit": "0.00",
            "credit": "0.00",
            "is_system_generated": True,
        },
        select_search_fields=["party__name", "document_type", "document_id"],
        select_label_func=lambda obj: f"{obj.party} - {obj.document_type}",
    )
)


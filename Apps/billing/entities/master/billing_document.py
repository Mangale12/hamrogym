from core.config import EntityConfig
from core.registry import register_entity
from ...datatables.billing_document_data_table import BillingDocumentDataTableView, BILLING_DOCUMENT_COLUMNS
from ...forms.billing_document_form import BillingDocumentForm
from ...models import BillingDocument


register_entity(
    EntityConfig(
        name="billing_document",
        url_path="billing-documents",
        verbose_name="Billing Document",
        model=BillingDocument,
        form_class=BillingDocumentForm,
        datatable_view=BillingDocumentDataTableView,
        fields=[
            # TODO: define fields
            # {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in BILLING_DOCUMENT_COLUMNS
            if key != "id"
        ],
        reset_defaults={},
    )
)

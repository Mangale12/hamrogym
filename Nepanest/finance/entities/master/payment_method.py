from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.payment_method_data_table import PaymentMethodDataTableView
from ...forms import PaymentMethodForm
from ...models import PaymentMethod


register_entity(
    EntityConfig(
        name="payment_method",
        url_path="payment-methods",
        verbose_name="Payment Method",
        model=PaymentMethod,
        form_class=PaymentMethodForm,
        datatable_view=PaymentMethodDataTableView,
        fields=[
            {"name": "code", "label": "Code", "type": "text", "required": True, "col": 3, "placeholder": "ESEWA"},
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 5, "placeholder": "eSewa"},
            {"name": "category", "label": "Category", "type": "static_select", "required": True, "col": 4, "options": PaymentMethod._meta.get_field("category").choices},
            {"name": "provider", "label": "Provider", "type": "text", "required": False, "col": 4, "placeholder": "NCHL / Fonepay / eSewa"},
            {"name": "sequence", "label": "Sequence", "type": "number", "required": True, "col": 2, "attributes": {"min": "0"}},
            {"name": "is_digital", "label": "Digital", "type": "checkbox", "required": False, "col": 2},
            {"name": "supports_online", "label": "Online", "type": "checkbox", "required": False, "col": 2},
            {"name": "supports_qr", "label": "QR", "type": "checkbox", "required": False, "col": 2},
            {"name": "requires_reference", "label": "Needs Ref", "type": "checkbox", "required": False, "col": 2},
            {"name": "is_default", "label": "Default", "type": "checkbox", "required": False, "col": 2},
            {"name": "is_active", "label": "Active", "type": "checkbox", "required": False, "col": 2, "default": True},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Optional notes about usage or settlement."},
        ],
        datatable_columns=[
            {"name": "code", "title": "Code"},
            {"name": "name", "title": "Name"},
            {"name": "category", "title": "Category"},
            {"name": "provider", "title": "Provider", "render": "function(data){return data || '-';}"},
            {"name": "sequence", "title": "Sequence"},
            {"name": "is_digital", "title": "Digital", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "supports_online", "title": "Online", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "supports_qr", "title": "QR", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "requires_reference", "title": "Needs Ref", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_default", "title": "Default", "render": "function(data){return data ? 'Yes' : 'No';}"},
            {"name": "is_active", "title": "Active", "render": "function(data){return data ? 'Yes' : 'No';}"},
        ],
        reset_defaults={
            "category": "bank",
            "sequence": 1,
            "is_active": True,
        },
        select_search_fields=["code", "name", "category", "provider"],
        select_label_func=lambda obj: f"{obj.name} ({obj.code})",
    )
)

from decimal import Decimal, InvalidOperation

from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from ...datatables.payment_data_table import PAYMENT_COLUMNS, PaymentDataTableView
from ...forms import PaymentForm
from ...models import Payment, PaymentAllocation, PaymentStatus, PaymentType
from ...services import cancel_payment, post_payment, prepare_payment_for_save, synchronize_payment


def _to_decimal(value):
    raw = str(value or "").strip()
    if not raw:
        return Decimal("0.00")
    try:
        return Decimal(raw)
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def _to_sort_order(value):
    raw = str(value or "").strip()
    return int(raw) if raw.isdigit() else 1


def _prepare_payment(request, obj: Payment):
    prepare_payment_for_save(obj)


def _sync_payment(request, obj: Payment):
    synchronize_payment(obj)


def _post_payment(request, obj: Payment):
    posted = post_payment(obj, user=request.user)
    return {"message": f"Payment {posted.payment_no} posted successfully."}


def _cancel_payment(request, obj: Payment):
    cancelled = cancel_payment(obj, user=request.user)
    return {"message": f"Payment {cancelled.payment_no} cancelled successfully."}


PAYMENT_ALLOCATION_SECTION = {
    "title": "Payment Allocations",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "billing_document",
            "label": "Billing Document",
            "type": "select",
            "required": True,
            "url_name": "billing_document_select",
        },
        {"name": "amount", "label": "Amount", "type": "number", "required": True},
        {"name": "remarks", "label": "Remarks", "type": "text"},
        {"name": "sequence", "label": "Seq", "type": "number"},
    ],
}

PAYMENT_ALLOCATION_RELATION = RelatedDynamicSectionConfig(
    section_name="payment_allocations",
    related_model=PaymentAllocation,
    parent_field="payment",
    fields=["billing_document", "amount", "remarks", "sequence"],
    required_fields=["billing_document", "amount"],
    empty_check_fields=["billing_document", "amount", "remarks"],
    order_by="sequence",
    save_transformers={
        "amount": _to_decimal,
        "remarks": lambda value: (value or "").strip(),
        "sequence": _to_sort_order,
    },
)

_load_payment_allocations = build_related_section_loader(PAYMENT_ALLOCATION_RELATION)
_save_payment_allocations = build_related_section_saver(PAYMENT_ALLOCATION_RELATION)


register_entity(
    EntityConfig(
        name="payment",
        url_path="payments",
        verbose_name="Payment",
        model=Payment,
        form_class=PaymentForm,
        datatable_view=PaymentDataTableView,
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "required": False, "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "required": False, "col": 4, "url_name": "branch_select"},
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "required": False, "col": 4, "url_name": "fiscal_year_select"},
            {"name": "payment_no", "label": "Payment No", "type": "text", "required": False, "col": 3, "placeholder": "Auto-generated if blank"},
            {"name": "status", "label": "Status", "type": "static_select", "required": False, "col": 3, "options": PaymentStatus.choices, "attributes": {"disabled": "disabled"}},
            {"name": "payment_type", "label": "Payment Type", "type": "static_select", "required": True, "col": 3, "options": PaymentType.choices},
            {"name": "date", "label": "Payment Date", "type": "date", "required": True, "col": 3},
            {"name": "party", "label": "Party", "type": "select", "required": False, "col": 4, "url_name": "party_select"},
            {"name": "billing_profile", "label": "Billing Profile", "type": "select", "required": False, "col": 4, "url_name": "billing_profile_select"},
            {"name": "payment_method", "label": "Payment Method", "type": "select", "required": True, "col": 4, "url_name": "payment_method_select"},
            {"name": "currency", "label": "Currency", "type": "select", "required": True, "col": 3, "url_name": "currency_select"},
            {"name": "exchange_rate", "label": "Exchange Rate", "type": "number", "required": True, "col": 3, "attributes": {"step": "0.000001", "min": "0.000001"}},
            {"name": "amount", "label": "Amount", "type": "number", "required": True, "col": 3, "attributes": {"step": "0.01", "min": "0.01"}},
            {"name": "allocated_amount", "label": "Allocated", "type": "number", "required": False, "col": 3, "attributes": {"disabled": "disabled"}},
            {"name": "unapplied_amount", "label": "Unapplied", "type": "number", "required": False, "col": 3, "attributes": {"disabled": "disabled"}},
            {"name": "reference", "label": "External Reference", "type": "text", "required": False, "col": 4, "placeholder": "Cheque no / bank txn id / receipt ref"},
            {"name": "reference_date", "label": "Reference Date", "type": "date", "required": False, "col": 4},
            {"name": "journal_entry", "label": "Journal Entry", "type": "select", "required": False, "col": 4, "url_name": "journal_entry_select"},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12, "placeholder": "Narration, settlement notes, or internal comments."},
        ],
        dynamic_sections={
            "payment_allocations": PAYMENT_ALLOCATION_SECTION,
        },
        dynamic_sections_loader=_load_payment_allocations,
        dynamic_sections_saver=_save_payment_allocations,
        pre_save=_prepare_payment,
        post_save=_sync_payment,
        row_actions={
            "post": _post_payment,
            "cancel": _cancel_payment,
        },
        action_state_field="status",
        hide_edit_on_values=[PaymentStatus.POSTED, PaymentStatus.CANCELLED],
        hide_delete_on_values=[PaymentStatus.POSTED, PaymentStatus.CANCELLED],
        action_buttons=[
            {
                "action_name": "post",
                "title": "Post Payment",
                "label": "Post",
                "icon_class": "fas fa-check-circle",
                "class_name": "btn-outline-success",
                "button_class": "entity-post-action-btn",
                "confirm_text": "Post this payment? Posted payments update outstanding documents and can post the linked journal entry.",
                "success_message": "Payment posted successfully.",
                "hide_on_values": [PaymentStatus.POSTED, PaymentStatus.CANCELLED],
            },
            {
                "action_name": "cancel",
                "title": "Cancel Payment",
                "label": "Cancel",
                "icon_class": "fas fa-ban",
                "class_name": "btn-outline-danger",
                "button_class": "entity-post-action-btn",
                "confirm_text": "Cancel this payment? Any linked billing balances and journal entry will be reversed.",
                "success_message": "Payment cancelled successfully.",
                "hide_on_values": [PaymentStatus.CANCELLED],
            },
        ],
        datatable_columns=[
            {
                "name": key,
                "title": {
                    "payment_no": "Payment No",
                    "payment_type": "Payment Type",
                    "billing_profile": "Billing Profile",
                    "payment_method": "Method",
                    "allocated_amount": "Allocated",
                    "unapplied_amount": "Unapplied",
                    "journal_entry": "Journal Entry",
                }.get(key, key.replace("_", " ").title()),
            }
            for key, _accessor in PAYMENT_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "status": PaymentStatus.DRAFT,
            "payment_type": PaymentType.RECEIVE,
            "exchange_rate": "1.000000",
            "allocated_amount": "0.00",
            "unapplied_amount": "0.00",
        },
        datatable_options={"order": [[1, "desc"]]},
        select_search_fields=["payment_no", "reference", "party__name", "billing_profile__name"],
        select_label_func=lambda obj: f"{obj.payment_no or 'PAYMENT'} - {obj.amount}",
    )
)

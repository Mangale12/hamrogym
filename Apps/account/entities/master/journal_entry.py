from decimal import Decimal, InvalidOperation

from core.config import EntityConfig
from core.registry import register_entity
from core.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from ...datatables.journal_entry_data_table import JOURNAL_ENTRY_COLUMNS, JournalEntryDataTableView
from ...forms.journal_entry_form import JournalEntryForm
from ...models import JournalEntry, JournalEntrySide, JournalEntryStatus, JournalLine, PartnerType
from ...services import (
    cancel_journal_entry,
    post_journal_entry,
    prepare_journal_entry_for_save,
    synchronize_journal_entry,
)


def _to_decimal(value):
    raw = str(value or "").strip()
    if not raw:
        return Decimal("0.00")
    try:
        return Decimal(raw)
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def _to_optional_int(value):
    raw = str(value or "").strip()
    return int(raw) if raw.isdigit() else None


def _to_sort_order(value):
    raw = str(value or "").strip()
    return int(raw) if raw.isdigit() else 0


def _resolve_root_account(account):
    current = account
    while current and current.parent_id:
        current = current.parent
    return current


def _prepare_journal_entry(request, obj: JournalEntry):
    prepare_journal_entry_for_save(obj)


def _sync_journal_entry(request, obj: JournalEntry):
    synchronize_journal_entry(obj)


def _post_journal_entry(request, obj: JournalEntry):
    posted = post_journal_entry(obj, user=request.user)
    return {"message": f"Journal entry {posted.entry_no} posted successfully."}


def _cancel_journal_entry(request, obj: JournalEntry):
    was_posted = obj.status == JournalEntryStatus.POSTED
    cancelled = cancel_journal_entry(obj, user=request.user)
    message = (
        f"Journal entry {cancelled.entry_no} cancelled and reversed successfully."
        if was_posted
        else f"Draft journal entry {cancelled.entry_no} cancelled successfully."
    )
    return {"message": message}


JOURNAL_LINE_SECTION = {
    "title": "Journal Lines",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "account",
            "label": "Ledger Account",
            "type": "select",
            "required": True,
            "url_name": "journal_ledger_account_select",
        },
        {"name": "description", "label": "Description", "type": "text"},
        {
            "name": "entry_side",
            "label": "Entry Side",
            "type": "static_select",
            "options": JournalEntrySide.choices,
        },
        {"name": "amount", "label": "Amount", "type": "number"},
        {
            "name": "partner_type",
            "label": "Partner Type",
            "type": "static_select",
            "options": [("", "Select Type"), *PartnerType.choices],
        },
        {"name": "partner_id", "label": "Partner ID", "type": "number"},
        {"name": "cost_center", "label": "Cost Center", "type": "text"},
        {"name": "sort_order", "label": "Sort", "type": "number"},
    ],
}

JOURNAL_LINE_RELATION = RelatedDynamicSectionConfig(
    section_name="journal_lines",
    related_model=JournalLine,
    parent_field="journal_entry",
    fields=[
        "account",
        "description",
        "entry_side",
        "amount",
        "partner_type",
        "partner_id",
        "cost_center",
        "sort_order",
    ],
    required_fields=["account"],
    empty_check_fields=["account", "description", "amount", "partner_id", "cost_center"],
    order_by="sort_order",
    save_transformers={
        "description": lambda value: (value or "").strip(),
        "amount": _to_decimal,
        "partner_id": _to_optional_int,
        "cost_center": lambda value: (value or "").strip(),
        "sort_order": _to_sort_order,
    },
    row_load_hook=lambda item: {
        "root_account": str(_resolve_root_account(item.account).pk) if item.account_id else "",
    },
)

_load_journal_lines = build_related_section_loader(JOURNAL_LINE_RELATION)
_save_journal_lines = build_related_section_saver(JOURNAL_LINE_RELATION)


register_entity(
    EntityConfig(
        name="journal_entry",
        url_path="journal-entries",
        verbose_name="Journal Entry",
        model=JournalEntry,
        form_class=JournalEntryForm,
        datatable_view=JournalEntryDataTableView,
        template_name="account/journal_entry_index.html",
        fields=[
            {"name": "organization", "label": "Organization", "type": "select", "col": 4, "url_name": "organization_select"},
            {"name": "branch", "label": "Branch", "type": "select", "col": 4, "url_name": "branch_select"},
            {"name": "fiscal_year", "label": "Fiscal Year", "type": "select", "col": 4, "url_name": "fiscal_year_select"},
            {"name": "entry_no", "label": "Entry No", "type": "text", "required": False, "col": 3},
            {"name": "date", "label": "Date", "type": "date", "required": True, "col": 3},
            {"name": "voucher_type", "label": "Voucher Type", "type": "select", "required": True, "col": 3, "url_name": "voucher_type_select"},
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": False,
                "col": 3,
                "options": JournalEntryStatus.choices,
                "attributes": {"disabled": "disabled"},
            },
            {"name": "reference_no", "label": "Reference No", "type": "text", "col": 4},
            {"name": "narration", "label": "Narration", "type": "textarea", "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "col": 12},
        ],
        dynamic_sections={
            "journal_lines": JOURNAL_LINE_SECTION,
        },
        dynamic_sections_loader=_load_journal_lines,
        dynamic_sections_saver=_save_journal_lines,
        pre_save=_prepare_journal_entry,
        post_save=_sync_journal_entry,
        row_actions={
            "post": _post_journal_entry,
            "cancel": _cancel_journal_entry,
        },
        action_state_field="status",
        hide_edit_on_values=[JournalEntryStatus.POSTED, JournalEntryStatus.CANCELLED],
        hide_delete_on_values=[JournalEntryStatus.POSTED, JournalEntryStatus.CANCELLED],
        action_buttons=[
            {
                "action_name": "post",
                "title": "Post Entry",
                "label": "Post",
                "icon_class": "fas fa-check-circle",
                "class_name": "btn-outline-success",
                "button_class": "entity-post-action-btn",
                "confirm_text": "Post this journal entry? Only posted entries affect the ledger.",
                "success_message": "Journal entry posted successfully.",
                "hide_on_values": [JournalEntryStatus.POSTED, JournalEntryStatus.CANCELLED],
            },
            {
                "action_name": "cancel",
                "title": "Cancel Entry",
                "label": "Cancel",
                "icon_class": "fas fa-ban",
                "class_name": "btn-outline-danger",
                "button_class": "entity-post-action-btn",
                "confirm_text": "Cancel this journal entry? Posted entries will create reversal ledger postings.",
                "success_message": "Journal entry cancelled successfully.",
                "hide_on_values": [JournalEntryStatus.CANCELLED],
            },
        ],
        datatable_columns=[
            {
                "name": key,
                "title": {
                    "entry_no": "Entry No",
                    "voucher_type": "Voucher Type",
                    "reference_no": "Reference No",
                    "total_debit": "Total Debit",
                    "total_credit": "Total Credit",
                }.get(key, key.replace("_", " ").title()),
            }
            for key, _accessor in JOURNAL_ENTRY_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "status": JournalEntryStatus.DRAFT,
            "total_debit": "0.00",
            "total_credit": "0.00",
            "entry_no": "",
            "is_active": True,
        },
        datatable_options={"order": [[1, "desc"]]},
        select_search_fields=["entry_no", "reference_no", "voucher_type__name", "narration"],
        select_label_func=lambda obj: f"{obj.entry_no} - {obj.voucher_type.name}",
    )
)

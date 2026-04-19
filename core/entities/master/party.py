from core.config import EntityConfig
from core.registry import register_entity
from core.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from ...datatables.party_data_table import PartyDataTableView
from ...forms.party_form import PartyForm
from ...models import Party
from ...models.party import PartyAddress, PartyBankDetail, PartyContact, PartyFinancial


CONTACT_TYPE_OPTIONS = [("", "Select Type"), *PartyContact.CONTACT_TYPE]
ADDRESS_TYPE_OPTIONS = [("", "Select Type"), *PartyAddress.ADDRESS_TYPE]

CONTACTS_SECTION = {
    "title": "Contacts",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "contact_person", "label": "Contact Person", "type": "text", "required": False},
        {"name": "type", "label": "Type", "type": "static_select", "required": True, "options": CONTACT_TYPE_OPTIONS},
        {"name": "email", "label": "Email", "type": "text", "required": False},
        {"name": "phone", "label": "Phone", "type": "text", "required": False},
        {"name": "mobile", "label": "Mobile", "type": "text", "required": False},
        {"name": "is_primary", "label": "Primary", "type": "checkbox", "required": False},
    ],
}

ADDRESSES_SECTION = {
    "title": "Addresses",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "type", "label": "Type", "type": "static_select", "required": True, "options": ADDRESS_TYPE_OPTIONS},
        {"name": "address", "label": "Address", "type": "text", "required": False},
        {"name": "city", "label": "City", "type": "text", "required": False},
        {"name": "state", "label": "State", "type": "text", "required": False},
        {"name": "country", "label": "Country", "type": "text", "required": False},
        {"name": "is_default", "label": "Default", "type": "checkbox", "required": False},
    ],
}

FINANCIAL_SECTION = {
    "title": "Financial Details",
    "layout": "table",
    "allow_add": False,
    "allow_remove": False,
    "fields": [
        {"name": "credit_limit", "label": "Credit Limit", "type": "number", "required": False, "step": "0.01", "min": 0},
        {"name": "opening_balance", "label": "Opening Balance", "type": "number", "required": False, "step": "0.01"},
        {
            "name": "balance_type",
            "label": "Balance Type",
            "type": "static_select",
            "required": False,
            "options": PartyFinancial.BALANCE_TYPE_CHOICES,
        },
        {"name": "payment_terms", "label": "Payment Terms", "type": "text", "required": False},
    ],
}

BANK_DETAILS_SECTION = {
    "title": "Bank Details",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "bank_name", "label": "Bank Name", "type": "text", "required": True},
        {"name": "account_name", "label": "Account Name", "type": "text", "required": True},
        {"name": "account_number", "label": "Account Number", "type": "text", "required": True},
        {"name": "branch", "label": "Branch", "type": "text", "required": False},
        {"name": "ifsc_swift_code", "label": "IFSC/SWIFT", "type": "text", "required": False},
        {"name": "is_default", "label": "Default", "type": "checkbox", "required": False},
    ],
}

CONTACTS_SECTION_RELATION = RelatedDynamicSectionConfig(
    section_name="contacts",
    related_model=PartyContact,
    parent_field="party",
    fields=["contact_person", "type", "email", "phone", "mobile", "is_primary"],
    required_fields=["type"],
    bool_fields=["is_primary"],
    empty_check_fields=["contact_person", "type", "email", "phone", "mobile"],
    save_transformers={
        "contact_person": lambda value: (value or "").strip(),
        "type": lambda value: (value or "").strip(),
        "email": lambda value: (value or "").strip(),
        "phone": lambda value: (value or "").strip(),
        "mobile": lambda value: (value or "").strip(),
    },
)

ADDRESSES_SECTION_RELATION = RelatedDynamicSectionConfig(
    section_name="addresses",
    related_model=PartyAddress,
    parent_field="party",
    fields=["type", "address", "city", "state", "country", "is_default"],
    required_fields=["type"],
    bool_fields=["is_default"],
    empty_check_fields=["type", "address", "city", "state", "country"],
    save_transformers={
        "type": lambda value: (value or "").strip(),
        "address": lambda value: (value or "").strip(),
        "city": lambda value: (value or "").strip(),
        "state": lambda value: (value or "").strip(),
        "country": lambda value: (value or "").strip(),
    },
)

FINANCIAL_SECTION_RELATION = RelatedDynamicSectionConfig(
    section_name="financial",
    related_model=PartyFinancial,
    parent_field="party",
    fields=["credit_limit", "opening_balance", "balance_type", "payment_terms"],
    empty_check_fields=["credit_limit", "opening_balance", "payment_terms"],
    save_transformers={
        "credit_limit": lambda value: value if value not in (None, "") else 0,
        "opening_balance": lambda value: value if value not in (None, "") else 0,
        "balance_type": lambda value: (value or "dr").strip(),
        "payment_terms": lambda value: (value or "").strip(),
    },
    load_transformers={
        "credit_limit": lambda item: str(item.credit_limit),
        "opening_balance": lambda item: str(item.opening_balance),
    },
)

BANK_DETAILS_SECTION_RELATION = RelatedDynamicSectionConfig(
    section_name="bank_details",
    related_model=PartyBankDetail,
    parent_field="party",
    fields=["bank_name", "account_name", "account_number", "branch", "ifsc_swift_code", "is_default"],
    required_fields=["bank_name", "account_name", "account_number"],
    bool_fields=["is_default"],
    empty_check_fields=["bank_name", "account_name", "account_number", "branch", "ifsc_swift_code"],
    save_transformers={
        "bank_name": lambda value: (value or "").strip(),
        "account_name": lambda value: (value or "").strip(),
        "account_number": lambda value: (value or "").strip(),
        "branch": lambda value: (value or "").strip(),
        "ifsc_swift_code": lambda value: (value or "").strip(),
    },
)

_save_party_contacts = build_related_section_saver(CONTACTS_SECTION_RELATION)
_load_party_contacts = build_related_section_loader(CONTACTS_SECTION_RELATION)

_save_party_addresses = build_related_section_saver(ADDRESSES_SECTION_RELATION)
_load_party_addresses = build_related_section_loader(ADDRESSES_SECTION_RELATION)

_save_party_financial = build_related_section_saver(FINANCIAL_SECTION_RELATION)
_load_party_financial = build_related_section_loader(FINANCIAL_SECTION_RELATION)

_save_party_bank_details = build_related_section_saver(BANK_DETAILS_SECTION_RELATION)
_load_party_bank_details = build_related_section_loader(BANK_DETAILS_SECTION_RELATION)


def _load_party_dynamic_sections(party, request=None):
    data = {}
    data.update(_load_party_contacts(party, request))
    data.update(_load_party_addresses(party, request))
    data.update(_load_party_financial(party, request))
    data.update(_load_party_bank_details(party, request))
    return data


def _save_party_dynamic_sections(request, party):
    _save_party_contacts(request, party)
    _save_party_addresses(request, party)
    _save_party_financial(request, party)
    _save_party_bank_details(request, party)


register_entity(
    EntityConfig(
        name="party",
        url_path="parties",
        verbose_name="Party",
        model=Party,
        form_class=PartyForm,
        datatable_view=PartyDataTableView,
        fields=[],
        tabs=[
            {
                "key": "basic",
                "label": "Basic",
                "fields": [
                    {
                        "name": "name",
                        "label": "Party Name",
                        "type": "text",
                        "required": True,
                        "col": 6,
                        "placeholder": "ABC Traders",
                    },
                    {
                        "name": "display_name",
                        "label": "Display Name",
                        "type": "text",
                        "required": False,
                        "col": 6,
                        "placeholder": "ABC Traders Pvt. Ltd.",
                    },
                    {
                        "name": "party_type",
                        "label": "Party Type",
                        "type": "select",
                        "required": True,
                        "col": 6,
                        "url_name": "party_type_select",
                    },
                    {
                        "name": "category",
                        "label": "Category",
                        "type": "static_select",
                        "required": True,
                        "col": 6,
                        "options": Party.PARTY_CATEGORY,
                    },
                    {
                        "name": "pan_number",
                        "label": "PAN Number",
                        "type": "text",
                        "required": False,
                        "col": 4,
                        "placeholder": "123456789",
                    },
                    {
                        "name": "vat_number",
                        "label": "VAT Number",
                        "type": "text",
                        "required": False,
                        "col": 4,
                        "placeholder": "VAT-001",
                    },
                    {
                        "name": "registration_number",
                        "label": "Registration Number",
                        "type": "text",
                        "required": False,
                        "col": 4,
                        "placeholder": "REG-001",
                    },
                    {
                        "name": "is_active",
                        "label": "Active",
                        "type": "checkbox",
                        "required": False,
                        "col": 4,
                        "default": True,
                    },
                    {
                        "name": "remarks",
                        "label": "Remarks",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                        "placeholder": "Optional notes",
                    },
                ],
            },
            {
                "key": "contacts",
                "label": "Contacts",
                "fields": [],
                "sections": ["contacts"],
                "requires_id": True,
            },
            {
                "key": "addresses",
                "label": "Addresses",
                "fields": [],
                "sections": ["addresses"],
                "requires_id": True,
            },
            {
                "key": "financial",
                "label": "Financial",
                "fields": [],
                "sections": ["financial"],
                "requires_id": True,
            },
            {
                "key": "bank_details",
                "label": "Bank Details",
                "fields": [],
                "sections": ["bank_details"],
                "requires_id": True,
            },
        ],
        dynamic_sections={
            "contacts": CONTACTS_SECTION,
            "addresses": ADDRESSES_SECTION,
            "financial": FINANCIAL_SECTION,
            "bank_details": BANK_DETAILS_SECTION,
        },
        dynamic_sections_loader=_load_party_dynamic_sections,
        dynamic_sections_saver=_save_party_dynamic_sections,
        datatable_columns=[
            {"name": "name", "title": "Name"},
            {"name": "display_name", "title": "Display Name"},
            {"name": "party_type", "title": "Party Type"},
            {"name": "category", "title": "Category"},
            {"name": "pan_number", "title": "PAN Number"},
            {"name": "vat_number", "title": "VAT Number"},
            {
                "name": "is_active",
                "title": "Active",
                "render": "function(data){return data ? 'Yes' : 'No';}",
            },
        ],
        reset_defaults={"is_active": True, "category": "individual"},
        select_search_fields=[
            "name",
            "display_name",
            "pan_number",
            "vat_number",
            "registration_number",
            "party_type__name",
        ],
        select_label_func=lambda obj: obj.display_name or obj.name,
    )
)

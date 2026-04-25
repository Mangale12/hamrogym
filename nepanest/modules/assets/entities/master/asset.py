from django.core.exceptions import ValidationError
from django.utils import timezone

from nepanest.modules.assets.models.asset import AssetDocument
from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.helpers.context import get_current_branch_id, get_current_fiscal_year_id
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)
from nepanest.foundation.fiscal import FiscalYear
from nepanest.foundation.organization import Branch
from ...datatables.asset_data_table import AssetDataTableView, ASSET_COLUMNS
from ...forms.asset_form import AssetForm
from ...models import Asset
from ...services import generate_asset_depreciation_schedule

ASSET_DOCUMENT_SECTION = {
    "title": "Asset Documents",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {
            "name": "document_type",
            "label": "Document Type",
            "type": "text",
            "required": True,
            "col": 6,
        },
        {
            "name": "file_path",
            "label": "File",
            "type": "file",
            "required": True,
            "col": 6,
        },
    ],
}

ASSET_DOCUMENT_RELATION = RelatedDynamicSectionConfig(
    section_name="asset_documents",
    related_model=AssetDocument,
    parent_field="asset",
    fields=["document_type", "file_path"],
    required_fields=[
        "document_type",
        "file_path",
    ],
    empty_check_fields=[
        "document_type",
        "file_path",
    ],
    include_files=True,
)

ASSET_DOCUMENT_RELATION_LOADER = build_related_section_loader(ASSET_DOCUMENT_RELATION)
ASSET_DOCUMENT_RELATION_SAVER = build_related_section_saver(ASSET_DOCUMENT_RELATION)


def _generate_depreciation_schedule(request, asset: Asset):
    branch_id = get_current_branch_id(request)
    fiscal_year_id = get_current_fiscal_year_id(request)

    branch = Branch.objects.select_related("organization").filter(pk=branch_id).first() if branch_id else None
    fiscal_year = FiscalYear.objects.filter(pk=fiscal_year_id).first() if fiscal_year_id else None
    if not branch:
        raise ValidationError("Active branch is required in session to generate depreciation schedule.")
    if not fiscal_year:
        raise ValidationError("Active fiscal year is required in session to generate depreciation schedule.")

    result = generate_asset_depreciation_schedule(
        asset,
        organization=branch.organization,
        branch=branch,
        fiscal_year=fiscal_year,
        through_date=fiscal_year.end_date if fiscal_year else timezone.localdate(),
    )
    return {
        "message": (
            f"Depreciation schedule generated for {asset.name}. "
            f"Created: {result['created']}, Updated: {result['updated']}, Skipped posted: {result['skipped']}."
        )
    }

register_entity(
    EntityConfig(
        name="asset",
        url_path="asset",
        verbose_name="Assets",
        model=Asset,
        form_class=AssetForm,
        datatable_view=AssetDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 6},
            {"name": "code", "label": "Code", "type": "text", "required": False, "col": 6},
            {
                "name": "category",
                "label": "Category",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "asset_category_select",
            },
            {
                "name": "asset_type",
                "label": "Asset Type",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "asset_type_select",
            },
            {
                "name": "brand",
                "label": "Brand",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "brand_select",
            },
            {"name": "model", "label": "Model", "type": "text", "required": False, "col": 6},
            {"name": "serial_number", "label": "Serial Number", "type": "text", "required": False, "col": 6},
            {"name": "bar_code", "label": "Bar Code", "type": "text", "required": False, "col": 6},
            {"name": "purchase_date", "label": "Purchase Date", "type": "date", "required": False, "col": 6},
            {"name": "purchase_cost", "label": "Purchase Cost", "type": "number", "required": False, "col": 6},
            {
                "name": "vendor",
                "label": "Vendor",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "asset_vendor_select",
            },
            {
                "name": "warranty_expiry_date",
                "label": "Warranty Expiry Date",
                "type": "date",
                "required": False,
                "col": 6,
            },
            {
                "name": "use_full_life_months",
                "label": "Use Full Life Months",
                "type": "number",
                "required": False,
                "col": 6,
            },
            {
                "name": "salvage_value",
                "label": "Salvage Value",
                "type": "number",
                "required": False,
                "col": 6,
            },
            {
                "name": "depreciation_start_date",
                "label": "Depreciation Start Date",
                "type": "date",
                "required": False,
                "col": 6,
            },
            {
                "name": "current_location",
                "label": "Current Location",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "location_select",
            },
            {
                "name": "current_department",
                "label": "Current Department",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "department_select",
            },
            {
                "name": "current_employee",
                "label": "Current Employee",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "user_select",
            },
            {
                "name": "status",
                "label": "Status",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "asset_status_select",
            },
            {
                "name": "condition",
                "label": "Condition",
                "type": "select",
                "required": False,
                "col": 6,
                "url_name": "asset_condition_select",
            },
            {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        dynamic_sections={
            "asset_documents": ASSET_DOCUMENT_SECTION,
        },
        dynamic_sections_loader=ASSET_DOCUMENT_RELATION_LOADER,
        dynamic_sections_saver=ASSET_DOCUMENT_RELATION_SAVER,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in ASSET_COLUMNS
            if key != "id"
        ],
        reset_defaults={"is_active": True},
        row_actions={
            "generate_depreciation_schedule": _generate_depreciation_schedule,
        },
        select_search_fields=[
            "name",
            "code",
            "serial_number",
            "bar_code",
            "category__name",
            "asset_type__name",
            "brand__name",
        ],
        select_label_field="name",
        action_buttons=[
            {
                "title": "Profile",
                "icon_class": "fas fa-eye",
                "class_name": "btn-outline-info",
                "href_url": "/core/asset/{id}/profile/",
            },
            {
                "action_name": "generate_depreciation_schedule",
                "title": "Generate Depreciation",
                "icon_class": "fas fa-calendar-plus",
                "class_name": "btn-outline-primary",
                "confirm_text": "Generate or refresh missing depreciation schedule lines for this asset up to the active fiscal year end?",
                "success_message": "Depreciation schedule generated successfully.",
            },
        ],
        show_view=False,
    )
)

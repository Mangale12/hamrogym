from core.datatables.views import BaseDataTableView
from ..models import Asset


ASSET_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("category", "category.name"),
    ("asset_type", "asset_type.name"),
    ("brand", "brand.name"),
    ("model", "model"),
    ("serial_number", "serial_number"),
    ("vendor", "vendor.name"),
    ("purchase_date", "purchase_date"),
    ("purchase_cost", "purchase_cost"),
    ("depreciation_start_date", "depreciation_start_date"),
    ("current_location", "current_location.name"),
    ("current_department", "current_department.name"),
    ("current_employee", lambda obj: obj.current_employee.get_full_name() or obj.current_employee.username if obj.current_employee else ""),
    ("status", "status.name"),
    ("condition", "condition.name"),
    ("is_active", "is_active"),
]


class AssetDataTableView(BaseDataTableView):
    model = Asset
    columns = ASSET_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "category__name",
        "asset_type__name",
        "brand__name",
        "model",
        "serial_number",
        "bar_code",
        "vendor__name",
        "purchase_date",
        "purchase_cost",
        "depreciation_start_date",
        "current_location__name",
        "current_department__name",
        "current_employee__username",
        "current_employee__first_name",
        "current_employee__last_name",
        "status__name",
        "condition__name",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "code",
        "category__name",
        "asset_type__name",
        "brand__name",
        "model",
        "serial_number",
        "vendor__name",
        "purchase_date",
        "purchase_cost",
        "depreciation_start_date",
        "current_location__name",
        "current_department__name",
        "current_employee__username",
        "status__name",
        "condition__name",
        "is_active",
    ]

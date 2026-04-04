from django.db.models import Q


def _normalize(value: str) -> str:
    return (value or "").strip().lower().replace(" ", "_").replace("-", "_")


def _resolve_asset_status(*, asset, codes):
    normalized_codes = [_normalize(code) for code in codes if code]
    if not normalized_codes:
        return None

    statuses = asset._meta.get_field("status").remote_field.model.objects.filter(is_active=True)
    for status in statuses:
        code_value = _normalize(getattr(status, "code", "") or "")
        name_value = _normalize(getattr(status, "name", "") or "")
        if code_value in normalized_codes or name_value in normalized_codes:
            return status
    return None


def sync_asset_state(asset) -> None:
    active_assignment = (
        asset.assignments.select_related("employee__user", "employee__department")
        .filter(status="active", return_date__isnull=True)
        .order_by("-assigned_date", "-id")
        .first()
    )
    has_open_maintenance = asset.maintenance_records.filter(
        ~Q(status="completed")
    ).exists()

    if active_assignment:
        employee = active_assignment.employee
        asset.current_employee = employee.user
        asset.current_department = employee.department
    else:
        asset.current_employee = None
        asset.current_department = None

    if has_open_maintenance:
        next_status = _resolve_asset_status(
            asset=asset,
            codes=["under_maintenance", "maintenance"],
        )
    elif active_assignment:
        next_status = _resolve_asset_status(
            asset=asset,
            codes=["assigned", "in_use"],
        )
    else:
        next_status = _resolve_asset_status(
            asset=asset,
            codes=["available"],
        )

    if next_status is not None:
        asset.status = next_status

    asset.save(update_fields=["current_employee", "current_department", "status", "updated_at"])

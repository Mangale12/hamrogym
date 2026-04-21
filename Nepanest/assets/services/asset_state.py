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
    latest_transfer = (
        asset.transfers.select_related("to_location", "to_department")
        .order_by("-transfer_date", "-id")
        .first()
    )
    has_open_maintenance = asset.maintenance_records.filter(
        ~Q(status="completed")
    ).exists()

    if latest_transfer and latest_transfer.to_location_id:
        asset.current_location = latest_transfer.to_location

    if active_assignment:
        employee = active_assignment.employee
        asset.current_employee = employee.user
        asset.current_department = employee.department
    else:
        asset.current_employee = None
        if latest_transfer and latest_transfer.to_department_id:
            asset.current_department = latest_transfer.to_department
        else:
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


def sync_asset_status_from_incident(incident) -> None:
    asset = incident.asset
    incident_code = _normalize(getattr(incident.incident_type, "code", "") or "")

    status_map = {
        "lost": ["lost"],
        "missing": ["missing", "lost"],
        "stolen": ["stolen", "lost"],
        "disposed": ["disposed"],
        "scrapped": ["scrapped", "disposed"],
        "damaged": ["under_maintenance", "maintenance", "damaged"],
        "breakdown": ["under_maintenance", "maintenance"],
    }
    codes = status_map.get(incident_code, [])
    next_status = _resolve_asset_status(asset=asset, codes=codes)

    destructive_codes = {"lost", "missing", "stolen", "disposed", "scrapped"}
    if incident_code in destructive_codes:
        asset.current_employee = None
        asset.current_department = None

    if next_status is not None:
        asset.status = next_status

    asset.save(update_fields=["current_employee", "current_department", "status", "updated_at"])

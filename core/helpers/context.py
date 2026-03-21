from core.models import FiscalYear
from core.helpers.helper import get_calendar_type, get_organization_settings


FISCAL_YEAR_SESSION_KEYS = (
    "fiscal_year_id",
    "active_fiscal_year_id",
    "current_fiscal_year_id",
)


def get_session_int(request, keys):
    for key in keys:
        value = request.session.get(key)
        if value in (None, ""):
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def get_current_fiscal_year_id(request):
    fiscal_year_id = get_session_int(request, FISCAL_YEAR_SESSION_KEYS)
    if fiscal_year_id:
        return fiscal_year_id

    current_fiscal_year = FiscalYear.objects.filter(is_current=True).order_by("-start_date", "-id").first()
    if current_fiscal_year:
        return current_fiscal_year.pk

    active_fiscal_year = FiscalYear.objects.filter(is_active=True).order_by("-start_date", "-id").first()
    return active_fiscal_year.pk if active_fiscal_year else None


def organization_context(request):
    calendar_type = get_calendar_type(request)
    return {
        "organization_settings": get_organization_settings(),
        "calendar_type": calendar_type,
        "is_bs_calendar": calendar_type == "BS",
        "is_ad_calendar": calendar_type == "AD",
    }

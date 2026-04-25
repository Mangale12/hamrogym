from datetime import date

from django.core.cache import cache
from nepali_datetime import date as bs_date

from nepanest.foundation.organization import OrganizationSettings


CALENDAR_SESSION_KEYS = (
    "calendar_type",
    "active_calendar_type",
    "organization_calendar_type",
)


def get_organization_settings():
    settings = cache.get("organization_settings")

    if not settings:
        settings = OrganizationSettings.objects.first()
        cache.set("organization_settings", settings, 3600)

    return settings


def _normalize_calendar_type(value):
    value = (value or "").strip().upper()
    return value if value in {"AD", "BS"} else None


def get_calendar_type(request=None):
    if request is not None:
        for key in CALENDAR_SESSION_KEYS:
            value = _normalize_calendar_type(request.session.get(key))
            if value:
                return value

    settings = get_organization_settings()
    calendar_type = "AD"

    if settings:
        calendar_type = _normalize_calendar_type(settings.calendar) or "AD"

    if request is not None:
        request.session["calendar_type"] = calendar_type

    return calendar_type


def is_bs_calendar(request=None):
    return get_calendar_type(request) == "BS"


def is_ad_calendar(request=None):
    return get_calendar_type(request) == "AD"


def ad_to_bs(ad_date):
    return bs_date.from_datetime_date(ad_date)


def bs_to_ad(bs_date_string):
    year, month, day = map(int, bs_date_string.split("-"))
    bs = bs_date(year, month, day)
    return bs.to_datetime_date()


def encode_date_for_display(date_value, request=None):
    if not date_value:
        return ""
    if get_calendar_type(request) == "BS":
        bs_value = ad_to_bs(date_value)
        return f"{bs_value.year:04d}-{bs_value.month:02d}-{bs_value.day:02d}"
    return date_value.strftime("%Y-%m-%d")


def encode_datetime_for_display(datetime_value, request=None):
    if not datetime_value:
        return ""
    return f"{encode_date_for_display(datetime_value.date(), request)} {datetime_value.strftime('%H:%M:%S')}"


def decode_date_for_save(date_value, request=None):
    if not date_value:
        return date_value
    if isinstance(date_value, date):
        return date_value
    if get_calendar_type(request) != "BS":
        return date_value
    return bs_to_ad(date_value)

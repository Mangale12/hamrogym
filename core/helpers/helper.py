from core.models import OrganizationSettings
from django.core.cache import cache
from nepali_datetime import date as bs_date
from datetime import date
def get_organization_settings():
    settings = cache.get("organization_settings")

    if not settings:
        settings = OrganizationSettings.objects.first()
        cache.set("organization_settings", settings, 3600)

    return settings


def get_calendar_type():
    settings = get_organization_settings()

    if not settings:
        return "AD"

    return settings.calendar_type


def is_bs_calendar():
    return get_calendar_type() == "BS"


def is_ad_calendar():
    return get_calendar_type() == "AD"


def ad_to_bs(ad_date):
    return bs_date.from_datetime_date(ad_date)


def bs_to_ad(bs_date_string):

    year, month, day = map(int, bs_date_string.split("-"))

    bs = bs_date(year, month, day)

    return bs.to_datetime_date()
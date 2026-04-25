import builtins

from nepanest.common.helpers.helper import (
    ad_to_bs,
    bs_to_ad,
    decode_date_for_save,
    encode_date_for_display,
    get_calendar_type,
    get_organization_settings,
    is_ad_calendar,
    is_bs_calendar,
)


builtins.get_organization_settings = get_organization_settings
builtins.calendar_type = get_calendar_type
builtins.is_bs = is_bs_calendar
builtins.is_ad = is_ad_calendar
builtins.ad_to_bs = ad_to_bs
builtins.bs_to_ad = bs_to_ad
builtins.encode_date_for_display = encode_date_for_display
builtins.decode_date_for_save = decode_date_for_save

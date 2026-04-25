from datetime import date

from nepali_datetime import date as bs_date


class DateConverter:
    @staticmethod
    def ad_to_bs(ad_date):
        return bs_date.from_datetime_date(ad_date)

    @staticmethod
    def bs_to_ad(bs_year, bs_month, bs_day):
        bs = bs_date(bs_year, bs_month, bs_day)
        return bs.to_datetime_date()

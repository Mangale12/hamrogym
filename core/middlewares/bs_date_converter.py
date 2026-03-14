from django.utils.deprecation import MiddlewareMixin
from core.utils.date_converter import DateConverter


class BSDateConverterMiddleware(MiddlewareMixin):

    # fields that should convert
    DATE_FIELDS = [
        "date",
        "start_date",
        "end_date",
        "dob",
    ]

    def process_request(self, request):

        if request.method in ["POST", "PUT", "PATCH"]:

            data = request.POST.copy()  # make mutable

            for field in self.DATE_FIELDS:

                if field in data and data[field]:

                    try:
                        year, month, day = map(int, data[field].split("-"))

                        ad_date = DateConverter.bs_to_ad(year, month, day)

                        data[field] = ad_date

                    except Exception:
                        pass

            request.POST = data
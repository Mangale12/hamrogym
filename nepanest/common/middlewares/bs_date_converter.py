from django.utils.deprecation import MiddlewareMixin

from nepanest.common.helpers.helper import decode_date_for_save, get_calendar_type
from nepanest.common.utils.date_converter import DateConverter


class BSDateConverterMiddleware(MiddlewareMixin):
    DATE_FIELDS = [
        "date",
        "start_date",
        "end_date",
        "dob",
        "date_from",
        "date_to",
    ]

    def process_request(self, request):
        if request.method in ["POST", "PUT", "PATCH"]:
            data = request.POST.copy()
            requested_fields = set(data.getlist("__bs_date_fields"))
            if not requested_fields and get_calendar_type(request) != "BS":
                return
            date_fields = requested_fields or set(self.DATE_FIELDS)

            for field in date_fields:
                if field in data and data[field]:
                    try:
                        ad_date = decode_date_for_save(data[field], request)
                        data[field] = ad_date
                    except Exception:
                        pass

            request.POST = data

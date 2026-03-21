from django.utils.deprecation import MiddlewareMixin
from core.helpers.helper import decode_date_for_save, get_calendar_type
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
            if get_calendar_type(request) != "BS":
                return

            data = request.POST.copy()  # make mutable
            requested_fields = set(data.getlist("__bs_date_fields"))
            date_fields = requested_fields or set(self.DATE_FIELDS)

            for field in date_fields:

                if field in data and data[field]:

                    try:
                        ad_date = decode_date_for_save(data[field], request)
                        data[field] = ad_date

                    except Exception:
                        pass

            request.POST = data

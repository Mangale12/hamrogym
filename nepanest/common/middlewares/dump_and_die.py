from django.utils.deprecation import MiddlewareMixin


class DumpAndDieMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        return getattr(exception, "_dd_response", None)

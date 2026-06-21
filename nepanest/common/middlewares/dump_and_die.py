from django.utils.deprecation import MiddlewareMixin

from nepanest.common.helpers.debug_helper import DumpAndDie


class DumpAndDieMiddleware(MiddlewareMixin):
    def __call__(self, request):
        try:
            return super().__call__(request)
        except DumpAndDie as exception:
            return exception._dd_response

    async def __acall__(self, request):
        try:
            return await super().__acall__(request)
        except DumpAndDie as exception:
            return exception._dd_response

    def process_exception(self, request, exception):
        return getattr(exception, "_dd_response", None)

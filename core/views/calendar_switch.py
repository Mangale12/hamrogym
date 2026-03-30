from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View


class CalendarSwitchView(View):
    allowed_methods = ["post"]

    def post(self, request, *args, **kwargs):
        calendar_type = (request.POST.get("calendar_type") or "").strip().upper()
        if calendar_type in {"AD", "BS"}:
            request.session["calendar_type"] = calendar_type
            request.session["active_calendar_type"] = calendar_type
            request.session.modified = True

        next_url = (request.POST.get("next") or "").strip()
        if not next_url:
            next_url = request.META.get("HTTP_REFERER", "")
        if not url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = "/"
        return redirect(next_url)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(self.allowed_methods)

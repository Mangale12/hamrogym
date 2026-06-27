from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View

from core.views.auth import RememberMeLoginView

from .forms import TenantAwareAuthenticationForm
from .context import TENANT_DATABASE_ALIAS_SESSION_KEY, TENANT_SESSION_KEY, clear_current_tenant


class TenantLoginView(RememberMeLoginView):
    template_name = "accounts/login.html"
    authentication_form = TenantAwareAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)

        tenant_code = form.cleaned_data.get("tenant_code", "").strip().lower()
        tenant_database_alias = getattr(form.request, "tenant_database_alias", None)
        
        self.request.session[TENANT_SESSION_KEY] = tenant_code
        self.request.session["gym_code"] = tenant_code

        if tenant_database_alias:
            self.request.session[TENANT_DATABASE_ALIAS_SESSION_KEY] = tenant_database_alias
            self.request.session["db_alias"] = tenant_database_alias

        self.request.session["tenant_name"] = _get_tenant_name(tenant_code)

        return response

    def form_invalid(self, form):
        clear_current_tenant()
        return super().form_invalid(form)


class TenantLogoutView(View):
    def get(self, request):
        return self._logout(request)

    def post(self, request):
        return self._logout(request)

    def _logout(self, request):
        clear_current_tenant()
        logout(request)
        request.session.flush()
        messages.success(request, "You have been logged out.")
        return redirect(settings.LOGOUT_REDIRECT_URL)


def _get_tenant_name(gym_code: str) -> str:
    try:
        from nepanest.platform.tenancy.models import Tenant
        return Tenant.objects.using("default").get(code=gym_code).name
    except Exception:
        return gym_code

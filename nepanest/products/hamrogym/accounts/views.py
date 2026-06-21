import logging
import django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View
from django.db import connection, connections

from nepanest.platform.tenancy.context import (
    TenantLookupError,
    resolve_tenant_by_code,
    set_current_tenant,
    clear_current_tenant,
    get_current_database_alias,
)

logger = logging.getLogger(__name__)


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        # Already logged in → go straight to dashboard
        if request.user.is_authenticated and request.session.get("gym_code"):
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(request, self.template_name)

    def post(self, request):
        gym_code = request.POST.get("gym_code", "").strip().lower()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        # --- Validate inputs ---
        if not all([gym_code, username, password]):
            return render(request, self.template_name, {
                "error":    "All fields are required.",
                "gym_code": gym_code,
                "username": username,
            })

        # --- Step 1: resolve tenant from shared registry ---
        try:
            tenant = resolve_tenant_by_code(gym_code)
        except TenantLookupError as exc:
            logger.error("Tenant lookup failed while authenticating %s @ %s: %s", username, gym_code, exc)
            return render(request, self.template_name, {
                "error":    "Unable to resolve workspace right now. Please try again later.",
                "gym_code": gym_code,
                "username": username,
            })
        if tenant is None:
            return render(request, self.template_name, {
                "error":    f'No account found for code "{gym_code}".',
                "gym_code": gym_code,
                "username": username,
            })

        # --- Step 2: set tenant context before authenticate() ---
        set_current_tenant(tenant)
        db_alias = get_current_database_alias()

        # --- Step 3: authenticate against tenant DB ---
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            clear_current_tenant()
            logger.warning(f"Failed login: {username} @ {gym_code}")
            return render(request, self.template_name, {
                "error":    "Invalid username or password.",
                "gym_code": gym_code,
                "username": username,
            })

        if not user.is_active:
            clear_current_tenant()
            return render(request, self.template_name, {
                "error":    "Your account is disabled. Contact your administrator.",
                "gym_code": gym_code,
                "username": username,
            })

        # --- Step 4: log in and store session ---
        login(request, user)

        request.session["tenant_code"] = gym_code
        request.session["db_alias"] = db_alias
        request.session["gym_code"] = gym_code
        request.session["tenant_name"] = _get_tenant_name(gym_code)
        request.session.set_expiry(60 * 60 * 8)  # 8 hours

        logger.info(f"Login success: {username} @ {gym_code}")

        # Respect ?next= redirect param
        next_url = request.POST.get("next") or request.GET.get("next") or settings.LOGIN_REDIRECT_URL
        return redirect(next_url)


class LogoutView(View):

    def get(self, request):
        # support GET logout for simple logout links
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
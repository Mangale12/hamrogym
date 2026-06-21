import logging
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

logger = logging.getLogger(__name__)

EXEMPT_PATHS = [
    "/accounts/login/",
    "/accounts/logout/",
    "/registry/",
    "/register/",
    "/platform/app-registry/",
    "/admin/",
    "/static/",
    "/media/",
    "/__debug__/",
    "/favicon.ico",
]


class TenantDatabaseMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from nepanest.common.utils.tenant_db import (
            get_tenant_db_alias,
            set_current_db,
            clear_current_db,
        )

        # Always clear first — safety net for previous request
        clear_current_db()
        self._set_request_defaults(request)

        # ── Registry/platform staff paths ─────────────────────────────────────
        # Staff and superusers accessing /registry/, /register/, /platform/
        # use the default (registry) database directly.
        # They have no tenant_code — skip ALL tenant enforcement for them.
        if self._is_registry_path(request.path):
            return self.get_response(request)

        # ── Exempt paths (login, static, media etc.) ──────────────────────────
        # Still resolve tenant context if available, but never block the request.
        if self._is_exempt(request.path):
            tenant_code = self._get_tenant_code(request)
            if tenant_code:
                db_alias = get_tenant_db_alias(tenant_code)
                if db_alias:
                    set_current_db(db_alias)
                    self._attach_tenant(request, db_alias, tenant_code)
            return self.get_response(request)

        # ── Staff/superuser on non-registry paths ─────────────────────────────
        # e.g. /admin/ is already exempt above, but if a staff user somehow
        # reaches a non-exempt path without a tenant_code, let them through
        # on the default DB rather than flushing their session.
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            tenant_code = self._get_tenant_code(request)
            if tenant_code:
                db_alias = get_tenant_db_alias(tenant_code)
                if db_alias:
                    set_current_db(db_alias)
                    self._attach_tenant(request, db_alias, tenant_code)
            # No tenant_code for staff is fine — they use default DB
            return self.get_response(request)

        # ── Normal tenant application requests ────────────────────────────────
        tenant_code = self._get_tenant_code(request)

        # Not logged in
        if not request.user.is_authenticated:
            if self._is_ajax(request):
                from django.http import JsonResponse
                return JsonResponse({"error": "Not authenticated"}, status=401)
            return redirect(settings.LOGIN_URL)

        # No tenant code in session
        if not tenant_code:
            request.session.flush()
            messages.warning(request, "Session expired. Please log in again.")
            return redirect(settings.LOGIN_URL)

        # Resolve tenant DB
        db_alias = get_tenant_db_alias(tenant_code)

        if not db_alias:
            request.session.flush()
            messages.error(request, "Account not found. Please contact support.")
            return redirect(settings.LOGIN_URL)

        self._attach_tenant(request, db_alias, tenant_code)
        set_current_db(db_alias)

        try:
            response = self.get_response(request)
        finally:
            clear_current_db()  # always clean up

        return response

    def _attach_tenant(self, request, db_alias: str, tenant_code: str) -> None:
        """Attach tenant info to the request object."""
        request.db_alias = db_alias
        request.gym_code = tenant_code
        request.tenant_code = tenant_code
        request.tenant_database_alias = db_alias

    def _set_request_defaults(self, request) -> None:
        request.db_alias = "default"
        request.gym_code = None
        request.tenant_code = None
        request.tenant_database_alias = None

    def _get_tenant_code(self, request) -> str | None:
        session = getattr(request, "session", {}) or {}
        return session.get("tenant_code") or session.get("gym_code")

    def _is_exempt(self, path: str) -> bool:
        return any(path.startswith(p) for p in EXEMPT_PATHS)

    def _is_ajax(self, request) -> bool:
        return request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def _is_registry_path(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in (
            "/registry/",
            "/register/",
            "/platform/app-registry/",
        ))
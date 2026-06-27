from __future__ import annotations

from .context import (
    TenantLookupError,
    get_current_database_alias,
    TENANT_SESSION_KEY,
    clear_current_tenant,
    resolve_tenant_by_code,
    set_current_tenant,
)


class TenantResolutionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        clear_current_tenant()

        try:
            if self._is_registry_path(request.path):
                self._clear_request_tenant(request)
                return self.get_response(request)

            tenant_code = request.session.get(TENANT_SESSION_KEY)
            try:
                tenant = resolve_tenant_by_code(tenant_code)
            except TenantLookupError:
                tenant = None

            if tenant is None:
                self._clear_request_tenant(request)
                if tenant_code:
                    request.session.pop(TENANT_SESSION_KEY, None)
            else:
                set_current_tenant(tenant)
                self._attach_request_tenant(request, tenant.code, get_current_database_alias(), tenant)

            return self.get_response(request)
        finally:
            clear_current_tenant()

    def _attach_request_tenant(self, request, tenant_code: str, database_alias: str, tenant=None) -> None:
        request.tenant = tenant
        request.tenant_code = tenant_code
        request.gym_code = tenant_code
        request.db_alias = database_alias
        request.tenant_database_alias = database_alias

    def _clear_request_tenant(self, request) -> None:
        request.tenant = None
        request.tenant_code = None
        request.gym_code = None
        request.db_alias = None
        request.tenant_database_alias = None

    def _is_registry_path(self, path: str) -> bool:
        return any(
            path == prefix or path.startswith(prefix + "/")
            for prefix in (
                "/registry",
                "/register",
                "/platform/app-registry",
                "/__debug__",
            )
        )

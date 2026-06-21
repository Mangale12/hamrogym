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

        if self._is_registry_path(request.path):
            request.tenant = None
            request.tenant_code = None
            request.tenant_database_alias = None
            return self.get_response(request)

        tenant_code = request.session.get(TENANT_SESSION_KEY)
        try:
            tenant = resolve_tenant_by_code(tenant_code)
        except TenantLookupError:
            tenant = None

        if tenant is None:
            request.tenant = None
            request.tenant_code = None
            request.tenant_database_alias = None
            if tenant_code:
                request.session.pop(TENANT_SESSION_KEY, None)
        else:
            set_current_tenant(tenant)
            request.tenant = tenant
            request.tenant_code = tenant.code
            request.tenant_database_alias = get_current_database_alias()

        return self.get_response(request)

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

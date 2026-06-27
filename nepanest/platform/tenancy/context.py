from __future__ import annotations

from contextvars import ContextVar

from django.conf import settings
from django.db import DatabaseError, connections

from ..app_registry.models import TenantDB


TENANT_SESSION_KEY = "tenant_code"
TENANT_DATABASE_ALIAS_SESSION_KEY = "tenant_db_alias"
TENANT_DEFAULT_DATABASE_ALIAS = getattr(settings, "TENANT_DEFAULT_DATABASE_ALIAS", "default")

_current_tenant_code: ContextVar[str | None] = ContextVar("current_tenant_code", default=None)
_current_database_alias: ContextVar[str] = ContextVar(
    "current_database_alias",
    default=TENANT_DEFAULT_DATABASE_ALIAS,
)


class TenantLookupError(RuntimeError):
    """Raised when the shared tenant table cannot be queried safely."""


def resolve_database_alias(database_alias: str | None) -> str:
    normalized_alias = (database_alias or "").strip()
    if normalized_alias and normalized_alias in settings.DATABASES:
        return normalized_alias
    return TENANT_DEFAULT_DATABASE_ALIAS


def set_current_database_alias(database_alias: str | None) -> None:
    _current_database_alias.set(resolve_database_alias(database_alias))


def _build_tenant_database_alias(tenant: object) -> str:
    return (
        getattr(tenant, "database_alias", None)
        or getattr(tenant, "db_alias", None)
        or f"db_erp_{getattr(tenant, 'code', '')}"
    )


def _register_tenant_database_alias(tenant: object) -> str:
    alias = _build_tenant_database_alias(tenant)
    db_config = settings.DATABASES.get("default", {}).copy()

    if hasattr(tenant, "db_name"):
        db_config["NAME"] = tenant.db_name
    if hasattr(tenant, "db_user"):
        db_config["USER"] = tenant.db_user
    if hasattr(tenant, "db_password"):
        db_config["PASSWORD"] = tenant.db_password
    if hasattr(tenant, "db_host"):
        db_config["HOST"] = tenant.db_host
    if hasattr(tenant, "db_port"):
        db_config["PORT"] = tenant.db_port

    settings.DATABASES[alias] = db_config
    connections.databases[alias] = db_config

    return alias


def clear_current_tenant() -> None:
    _current_tenant_code.set(None)
    set_current_database_alias(TENANT_DEFAULT_DATABASE_ALIAS)


def set_current_tenant(tenant: TenantDB | None) -> None:
    if tenant is None:
        clear_current_tenant()
        return

    _current_tenant_code.set(tenant.code)
    tenant_database_alias = _register_tenant_database_alias(tenant)
    set_current_database_alias(tenant_database_alias)


def get_current_tenant_code() -> str | None:
    return _current_tenant_code.get()


def get_current_database_alias() -> str:
    return _current_database_alias.get()


def get_current_tenant() -> TenantDB | None:
    tenant_code = get_current_tenant_code()
    if not tenant_code:
        return None

    return _get_active_tenant_by_code(tenant_code)


def resolve_tenant_by_code(tenant_code: str | None) -> TenantDB | None:
    if not tenant_code:
        return None
    normalized_code = tenant_code.strip()
    if not normalized_code:
        return None
    return _get_active_tenant_by_code(normalized_code, case_insensitive=True)


def _get_active_tenant_by_code(tenant_code: str, *, case_insensitive: bool = False) -> TenantDB | None:
    lookup = {"code__iexact" if case_insensitive else "code": tenant_code}
    try:
        return TenantDB.objects.using(TENANT_DEFAULT_DATABASE_ALIAS).filter(**lookup).first()
    except DatabaseError as exc:
        raise TenantLookupError(
            "Workspace lookup is temporarily unavailable because the shared tenant database is not ready."
        ) from exc

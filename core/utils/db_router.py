# utils/db_router.py
from nepanest.common.utils.tenant_db import get_current_db

class TenantRouter:
    """
    Routes all ORM queries to the current tenant's database.
    Falls back to 'default' if no tenant is set.

    Works automatically — your views don't need to call .using() anywhere.
    """

    # Models that should always use the default (registry) DB
    REGISTRY_APPS = ['tenancy', 'licensing', 'subscriptions', 'branding', 'app_registry']

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.REGISTRY_APPS:
            return 'default'
        return get_current_db()

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.REGISTRY_APPS:
            return 'default'
        return get_current_db()

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations within the same database
        db1 = get_current_db()
        db2 = get_current_db()
        return db1 == db2

    def allow_migrate(self, db, app_label, **hints):
        if app_label in self.REGISTRY_APPS:
            return db == 'default'
        return True
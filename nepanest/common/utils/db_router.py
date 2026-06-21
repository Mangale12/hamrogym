from nepanest.common.utils.tenant_db import get_current_db

REGISTRY_APPS = [
    "tenancy",
    "licensing",
    "subscriptions",
    "branding",
    "app_registry",
    "admin",
    "auth",
    "contenttypes",
    "sessions",
]

class TenantRouter:

    def db_for_read(self, model, **hints):
        if model._meta.app_label in REGISTRY_APPS:
            return "default"
        return get_current_db()

    def db_for_write(self, model, **hints):
        if model._meta.app_label in REGISTRY_APPS:
            return "default"
        return get_current_db()

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, **hints):
        return True
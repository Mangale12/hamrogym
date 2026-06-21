import threading
import logging
from django.db import connections, OperationalError
from django.conf import settings

logger = logging.getLogger(__name__)

_thread_local = threading.local()
_tenant_cache = {}
_cache_lock   = threading.Lock()


def get_tenant_db_alias(gym_code: str):
    if not gym_code:
        return None

    alias = f"db_erp_{gym_code}"

    if alias in _tenant_cache:
        return alias

    with _cache_lock:
        if alias in _tenant_cache:
            return alias

        # Step 1: Check tenant row exists in registry
        try:
            from nepanest.platform.app_registry.models import TenantDB
            tenant = TenantDB.objects.using("default").get(code=gym_code)
        except Exception as exc:
            logger.warning(f"Tenant not found in registry: {gym_code} — {exc}")
            return None
        # TODO: when per-tenant credentials are ready,
        #       override USER/PASSWORD/HOST/PORT from tenant model here.
        db_config = settings.DATABASES.get("default", {}).copy()
        db_config["NAME"] = tenant.db_name  # only this comes from TenantDB

        # Step 3: Check DB actually exists on MySQL server
        db_exists = _check_db_exists_on_server(
            db_name=db_config["NAME"],
            db_user=db_config["USER"],
            db_password=db_config["PASSWORD"],
            db_host=db_config["HOST"],
            db_port=db_config["PORT"],
        )

        if not db_exists:
            logger.error(
                f"Tenant '{gym_code}' found in registry "
                f"but database '{db_config['NAME']}' does NOT exist on server."
            )
            return None

        # Step 4: Register alias in Django connections
        settings.DATABASES[alias]    = db_config
        connections.databases[alias] = db_config
        _tenant_cache[alias]         = True

        logger.info(f"Registered DB alias: {alias} → {db_config['NAME']}")

    return alias


def _check_db_exists_on_server(
    db_name: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: str,
) -> bool:
    try:
        import MySQLdb
    except ImportError:
        import pymysql as MySQLdb

    conn = None
    try:
        conn = MySQLdb.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            password=db_password,
            connect_timeout=5,
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
            "WHERE SCHEMA_NAME = %s",
            (db_name,)
        )
        result = cursor.fetchone()
        cursor.close()

        if result:
            logger.info(f"Database '{db_name}' confirmed on server.")
            return True
        else:
            logger.warning(f"Database '{db_name}' NOT found on server.")
            return False

    except MySQLdb.OperationalError as e:
        logger.error(f"Cannot connect to MySQL server: {e}")
        return False
    except Exception as e:
        logger.error(f"DB existence check failed: {e}")
        return False
    finally:
        if conn:
            conn.close()


def _test_db_connection(alias: str) -> bool:
    try:
        conn = connections[alias]
        conn.ensure_connection()
        logger.info(f"Connection test passed for alias: {alias}")
        return True
    except OperationalError as e:
        logger.error(f"Connection test failed for alias '{alias}': {e}")
        return False


def set_current_db(alias: str):
    _thread_local.db_alias = alias


def get_current_db() -> str:
    return getattr(_thread_local, "db_alias", None) or "default"


def clear_current_db():
    if hasattr(_thread_local, "db_alias"):
        delattr(_thread_local, "db_alias")


def invalidate_tenant_cache(gym_code: str):
    """Call this when a tenant DB config changes."""
    alias = f"db_erp_{gym_code}"
    with _cache_lock:
        _tenant_cache.pop(alias, None)
        if alias in settings.DATABASES:
            del settings.DATABASES[alias]
        try:
            connections[alias].close()
        except Exception:
            pass
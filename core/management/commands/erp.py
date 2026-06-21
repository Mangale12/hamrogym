from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from django import db
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


# ── Django built-in app labels ────────────────────────────────────────────────
# These must be migrated first on every database so auth, sessions,
# contenttypes, and admin tables exist before any project code runs.
DJANGO_BUILTIN_LABELS = [
    "contenttypes",   # required by everything — migrate first
    "auth",           # users, groups, permissions
    "admin",          # django admin log
    "sessions",       # session table
    # "messages" intentionally excluded — no DB migrations (in-memory framework)
    # "staticfiles" intentionally excluded — no DB migrations
]

# ── nepanest platform labels ──────────────────────────────────────────────────
PLATFORM_LABELS = [
    "tenancy",        # nepanest.platform.tenancy
    "app_registry",   # nepanest.platform.app_registry  (registry ERD models)
]

# ── nepanest module labels ────────────────────────────────────────────────────
MODULE_LABELS = [
    "core",
    "crm",
    "people",
    "hr",
    "assets",
    "finance",
    "billing",
    "account",
    "task",
]

# Final ordered list — order matters: builtins → platform → modules
PROJECT_MODULE_LABELS = DJANGO_BUILTIN_LABELS + PLATFORM_LABELS + MODULE_LABELS


@dataclass(frozen=True)
class DatabaseChoice:
    alias: str
    name: str


class Command(BaseCommand):
    help = "ERP management entrypoint. Use `manage.py erp migrate` to run module/database migrations."

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="erp_action", required=True)

        migrate_parser = subparsers.add_parser(
            "migrate",
            help="Migrate one or more project modules across selected db_erp_* databases.",
        )
        migrate_parser.add_argument(
            "--modules",
            default="interactive",
            help=(
                "Module selection: "
                "  'all'         — every module including Django builtins, "
                "  'builtins'    — only Django built-in apps (auth/sessions/etc), "
                "  'platform'    — only nepanest platform apps, "
                "  'modules'     — only nepanest business modules, "
                "  comma-separated labels or numbers, "
                "  or 'interactive' prompt."
            ),
        )
        migrate_parser.add_argument(
            "--database",
            default="interactive",
            help="Database selection: all, comma-separated database names/aliases, or interactive prompt.",
        )
        migrate_parser.add_argument(
            "--force",
            action="store_true",
            help="Skip the final confirmation prompt.",
        )
        migrate_parser.add_argument(
            "--noinput",
            action="store_true",
            help="Do not prompt interactively. Requires explicit --modules and --database selections.",
        )
        migrate_parser.add_argument("--fake", action="store_true")
        migrate_parser.add_argument("--fake-initial", action="store_true")
        migrate_parser.add_argument("--run-syncdb", action="store_true")
        migrate_parser.add_argument("--plan", action="store_true")
        migrate_parser.add_argument("--check", action="store_true")
        migrate_parser.add_argument("--prune", action="store_true")

    def handle(self, *args, **options):
        action = options["erp_action"]
        if action != "migrate":
            raise CommandError(f"Unsupported ERP action: {action}")

        modules = self._select_modules(options["modules"], noinput=options["noinput"])
        databases = self._select_databases(options["database"], noinput=options["noinput"])

        if not options["force"]:
            self._confirm_execution(modules, databases, options)

        for database in databases:
            database = self._ensure_database_alias(database)
            self.stdout.write(self.style.MIGRATE_HEADING(f"\nDatabase: {database.alias} [{database.name}]"))

            if modules == ["all"]:
                # Step 1 — always migrate builtins first
                self.stdout.write(self.style.MIGRATE_LABEL("  [1/2] Migrating Django built-ins..."))
                for label in DJANGO_BUILTIN_LABELS:
                    self._run_migrate(label, database, options)

                # Step 2 — then migrate everything else
                self.stdout.write(self.style.MIGRATE_LABEL("  [2/2] Migrating all apps..."))
                call_command(
                    "migrate",
                    database=database.alias,
                    fake=options["fake"],
                    fake_initial=options["fake_initial"],
                    run_syncdb=options["run_syncdb"],
                    plan=options["plan"],
                    check=options["check"],
                    prune=options["prune"],
                    verbosity=options["verbosity"],
                )
                continue

            for module_label in modules:
                self._run_migrate(module_label, database, options)

    def _run_migrate(self, module_label: str, database: DatabaseChoice, options: dict) -> None:
        self.stdout.write(f"  → migrating {module_label}")
        call_command(
            "migrate",
            module_label,
            database=database.alias,
            fake=options["fake"],
            fake_initial=options["fake_initial"],
            run_syncdb=options["run_syncdb"],
            plan=options["plan"],
            check=options["check"],
            prune=options["prune"],
            verbosity=options["verbosity"],
        )

    def _select_modules(self, raw_value: str, *, noinput: bool) -> list[str]:
        # Handle shortcut group keywords
        if raw_value == "builtins":
            return list(DJANGO_BUILTIN_LABELS)
        if raw_value == "platform":
            return list(PLATFORM_LABELS)
        if raw_value == "modules":
            return list(MODULE_LABELS)

        available = self._available_modules()
        self._print_modules(available)

        if raw_value == "all":
            return ["all"]

        if raw_value != "interactive":
            return self._normalize_module_selection(raw_value, available)

        if noinput:
            raise CommandError("Interactive module selection requested, but --noinput was provided.")

        while True:
            choice = input("Select modules (all / builtins / platform / modules / comma-separated numbers): ").strip()
            if choice:
                try:
                    return self._normalize_module_selection(choice, available)
                except CommandError as exc:
                    self.stdout.write(self.style.ERROR(str(exc)))

    def _select_databases(self, raw_value: str, *, noinput: bool) -> list[DatabaseChoice]:
        available = self._available_databases()
        self._print_databases(available)

        if raw_value == "all":
            return available

        if raw_value != "interactive":
            return self._normalize_database_selection(raw_value, available)

        if noinput:
            raise CommandError("Interactive database selection requested, but --noinput was provided.")

        while True:
            choice = input("Select databases (all or comma-separated numbers/names like 1,2): ").strip()
            if choice:
                try:
                    return self._normalize_database_selection(choice, available)
                except CommandError as exc:
                    self.stdout.write(self.style.ERROR(str(exc)))

    def _confirm_execution(self, modules: list[str], databases: list[DatabaseChoice], options) -> None:
        module_text = "all modules" if modules == ["all"] else ", ".join(modules)
        database_text = ", ".join(f"{item.alias} [{item.name}]" for item in databases)
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("About to run migrations"))
        self.stdout.write(f"  modules:   {module_text}")
        self.stdout.write(f"  databases: {database_text}")
        if options["fake"]:
            self.stdout.write("  mode:      fake")
        if options["plan"]:
            self.stdout.write("  mode:      plan")

        confirmation = input('Type "FORCE" to continue: ').strip()
        if confirmation != "FORCE":
            raise CommandError("Migration cancelled by user.")

    def _available_modules(self) -> list[tuple[str, str]]:
        modules: list[tuple[str, str]] = []
        for label in PROJECT_MODULE_LABELS:
            try:
                app_config = apps.get_app_config(label)
            except LookupError:
                continue
            modules.append((app_config.label, app_config.verbose_name or app_config.label))
        return modules

    def _available_databases(self) -> list[DatabaseChoice]:
        discovered = self._discover_database_names()
        choices = [self._database_choice_for_name(db_name) for db_name in discovered]
        choices.sort(key=lambda item: (item.name, item.alias))
        if not choices:
            raise CommandError("No databases were found whose NAME starts with 'db_erp_'.")
        return choices

    def _print_modules(self, modules: list[tuple[str, str]]) -> None:
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Available modules"))
        self.stdout.write("  all.       all modules (builtins + platform + business)")
        self.stdout.write("  builtins.  Django built-ins only (auth, sessions, contenttypes, admin)")
        self.stdout.write("  platform.  nepanest platform only (tenancy, app_registry)")
        self.stdout.write("  modules.   nepanest business modules only")
        for index, (label, verbose_name) in enumerate(modules, start=1):
            self.stdout.write(f"  {index:>2}. {label:<20} ({verbose_name})")

    def _print_databases(self, databases: list[DatabaseChoice]) -> None:
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Available databases"))
        self.stdout.write("  all. all databases")
        for index, database in enumerate(databases, start=1):
            self.stdout.write(f"  {index:>2}. {database.alias:<20} ({database.name})")

    def _normalize_module_selection(self, raw_value: str, available: list[tuple[str, str]]) -> list[str]:
        # Handle group shortcuts inside comma list too
        if raw_value.strip() == "builtins":
            return list(DJANGO_BUILTIN_LABELS)
        if raw_value.strip() == "platform":
            return list(PLATFORM_LABELS)
        if raw_value.strip() == "modules":
            return list(MODULE_LABELS)

        tokens = [token.strip() for token in raw_value.split(",") if token.strip()]
        if not tokens:
            raise CommandError("No module selection provided.")

        lookup = {str(index): label for index, (label, _) in enumerate(available, start=1)}
        lookup.update({label: label for label, _ in available})

        resolved: list[str] = []
        for token in tokens:
            if token == "all":
                return ["all"]
            label = lookup.get(token)
            if not label:
                raise CommandError(f"Unknown module selection: {token!r}")
            if label not in resolved:
                resolved.append(label)
        return resolved

    def _normalize_database_selection(self, raw_value: str, available: list[DatabaseChoice]) -> list[DatabaseChoice]:
        tokens = [token.strip() for token in raw_value.split(",") if token.strip()]
        if not tokens:
            raise CommandError("No database selection provided.")

        lookup: dict[str, DatabaseChoice] = {}
        for index, database in enumerate(available, start=1):
            lookup[str(index)] = database
            lookup[database.alias] = database
            lookup[database.name] = database

        resolved: list[DatabaseChoice] = []
        for token in tokens:
            if token == "all":
                return available
            database = lookup.get(token)
            if not database:
                raise CommandError(f"Unknown database selection: {token!r}")
            if database not in resolved:
                resolved.append(database)
        return resolved

    def _discover_database_names(self) -> list[str]:
        try:
            driver = self._load_mysql_driver()
        except CommandError:
            return self._configured_database_names()

        db_settings = settings.DATABASES.get("default", {})
        host = db_settings.get("HOST") or "127.0.0.1"
        port = int(db_settings.get("PORT") or 3306)
        user = db_settings.get("USER") or "root"
        password = db_settings.get("PASSWORD") or ""

        try:
            connection = driver.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                connect_timeout=5,
            )
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Could not connect to MySQL server for discovery: {exc}"))
            return self._configured_database_names()

        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
                "WHERE SCHEMA_NAME LIKE %s "
                "ORDER BY SCHEMA_NAME",
                ("db_erp\\_%",),
            )
            names = [row[0] for row in cursor.fetchall()]
            cursor.close()
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Could not query MySQL database list: {exc}"))
            names = self._configured_database_names()
        finally:
            connection.close()

        return self._merge_database_names(names)

    def _configured_database_names(self) -> list[str]:
        names: list[str] = []
        for config in settings.DATABASES.values():
            db_name = config.get("NAME", "")
            if isinstance(db_name, str) and db_name.startswith("db_erp_"):
                names.append(db_name)
        return self._merge_database_names(names)

    def _merge_database_names(self, names: Iterable[str]) -> list[str]:
        return sorted({name for name in names if isinstance(name, str) and name.startswith("db_erp_")})

    def _database_choice_for_name(self, database_name: str) -> DatabaseChoice:
        for alias, config in settings.DATABASES.items():
            if config.get("NAME") == database_name:
                return DatabaseChoice(alias=alias, name=database_name)
        return DatabaseChoice(alias=database_name, name=database_name)

    def _load_mysql_driver(self):
        try:
            import MySQLdb  # type: ignore
            return MySQLdb
        except ImportError:
            try:
                import pymysql  # type: ignore
                return pymysql
            except ImportError as exc:
                raise CommandError(
                    "MySQL driver not available. Install mysqlclient or PyMySQL to discover databases."
                ) from exc

    def _ensure_database_alias(self, choice: DatabaseChoice) -> DatabaseChoice:
        if choice.alias in settings.DATABASES and settings.DATABASES[choice.alias].get("NAME") == choice.name:
            return choice

        base_config = settings.DATABASES.get("default", {}).copy()
        if not base_config:
            raise CommandError("Default database configuration is missing.")

        base_config["NAME"] = choice.name
        settings.DATABASES[choice.alias] = base_config
        db.connections.databases[choice.alias] = base_config
        return choice
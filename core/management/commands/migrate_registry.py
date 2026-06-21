from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run migrations for the registry database alias."

    def add_arguments(self, parser):
        parser.add_argument("app_label", nargs="?", help="Optional app label to migrate, e.g. app_registry")
        parser.add_argument("migration_name", nargs="?", help="Optional migration name, e.g. 0001_initial")
        parser.add_argument(
            "--database",
            default="default",
            help="Database alias to migrate. Defaults to the shared registry database alias.",
        )
        parser.add_argument("--fake", action="store_true", help="Mark migrations as run without executing them")
        parser.add_argument("--fake-initial", action="store_true", help="Fake initial migrations if tables already exist")
        parser.add_argument("--run-syncdb", action="store_true", help="Create tables for apps without migrations")
        parser.add_argument("--plan", action="store_true", help="Show the migration plan without applying it")
        parser.add_argument("--check", action="store_true", help="Check for conflicts before running")
        parser.add_argument("--prune", action="store_true", help="Prune stale migration records")
        parser.add_argument("--noinput", action="store_true", help="Do not prompt for input")

    def handle(self, *args, **options):
        migrate_args = [arg for arg in (options["app_label"], options["migration_name"]) if arg]

        call_command(
            "migrate",
            *migrate_args,
            database=options["database"],
            fake=options["fake"],
            fake_initial=options["fake_initial"],
            run_syncdb=options["run_syncdb"],
            plan=options["plan"],
            check=options["check"],
            prune=options["prune"],
            interactive=not options["noinput"],
            verbosity=options["verbosity"],
        )

from django.core.management.base import BaseCommand, CommandError
from django.db import models

from core.models import Branch

from ...models import GymFacility
from ...seed_data import COMMON_GYM_FACILITIES


class Command(BaseCommand):
    help = "Seed common gym facilities for Hamro Gym branches."

    def add_arguments(self, parser):
        parser.add_argument(
            "--branch",
            dest="branch_lookup",
            default="",
            help="Optional branch name or code. If omitted, seeds all branches.",
        )

    def handle(self, *args, **options):
        branch_lookup = (options.get("branch_lookup") or "").strip()

        branches = Branch.objects.all().order_by("organization__name", "name")
        if branch_lookup:
            branches = branches.filter(models.Q(name__iexact=branch_lookup) | models.Q(code__iexact=branch_lookup))

        branches = list(branches)
        if not branches:
            raise CommandError("No branches found. Create a branch first or pass a valid --branch value.")

        created_count = 0
        updated_count = 0

        for branch in branches:
            for facility in COMMON_GYM_FACILITIES:
                obj, created = GymFacility.objects.update_or_create(
                    branch=branch,
                    name=facility["name"],
                    defaults={
                        "organization": branch.organization,
                        "remarks": facility["remarks"],
                        "is_active": True,
                    },
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created {obj.name} for {branch.name}"))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"Updated {obj.name} for {branch.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Gym facility seeding completed. Created: {created_count}, Updated: {updated_count}"
            )
        )

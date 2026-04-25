import json
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed all ErpEntity records from JSON in core/fixtures dynamically"

    def handle(self, *args, **kwargs):
        fixtures_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "core" / "fixtures"
        json_file = fixtures_dir / "erp_entities.json"

        if not json_file.exists():
            self.stdout.write(self.style.ERROR(f"JSON file not found: {json_file}"))
            return

        with open(json_file, "r", encoding="utf-8") as f:
            entities = json.load(f)

        for entity in entities:
            code = entity.get("code")
            if not code:
                continue

            obj, created = apps.get_model("core", "ErpEntity").objects.get_or_create(
                code=code,
                defaults={
                    "name": entity.get("name", ""),
                    "module": entity.get("module", ""),
                    "app_label": entity.get("app_label", ""),
                    "model_name": entity.get("model_name", ""),
                    "remarks": entity.get("remarks", ""),
                    "is_active": True,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {obj.name}"))
            else:
                updated_fields = {}
                for field in ["name", "module", "app_label", "model_name", "remarks"]:
                    new_value = entity.get(field, "")
                    old_value = getattr(obj, field, "")
                    if new_value != old_value:
                        updated_fields[field] = {"old": old_value, "new": new_value}
                        setattr(obj, field, new_value)

                if updated_fields:
                    obj.save()
                    self.stdout.write(self.style.WARNING(f"Updated {obj.name}"))
                else:
                    self.stdout.write(self.style.NOTICE(f"No changes: {obj.name}"))

        self.stdout.write(self.style.SUCCESS("ERP Entities seeding completed."))

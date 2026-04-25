from pathlib import Path

from django.apps import AppConfig


class PeopleModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nepanest.modules.people"
    label = "people"
    verbose_name = "People"
    path = str(Path(__file__).resolve().parent)

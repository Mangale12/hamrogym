from pathlib import Path

from django.apps import AppConfig


class HumanResourcesModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nepanest.modules.human_resources"
    label = "hr"
    path = str(Path(__file__).resolve().parent)

from pathlib import Path

from django.apps import AppConfig


class BillingModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nepanest.modules.billing"
    label = "billing"
    path = str(Path(__file__).resolve().parent)

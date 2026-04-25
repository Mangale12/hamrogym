from pathlib import Path

from django.apps import AppConfig


class FinanceModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nepanest.modules.finance"
    label = "finance"
    path = str(Path(__file__).resolve().parent)

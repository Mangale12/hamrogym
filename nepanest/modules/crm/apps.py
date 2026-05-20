from pathlib import Path

from django.apps import AppConfig


class CRMModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nepanest.modules.crm"
    label = "crm"
    verbose_name = "CRM"
    path = str(Path(__file__).resolve().parent)

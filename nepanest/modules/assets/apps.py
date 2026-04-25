from pathlib import Path

from django.apps import AppConfig


class AssetsModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nepanest.modules.assets"
    label = "assets"
    path = str(Path(__file__).resolve().parent)

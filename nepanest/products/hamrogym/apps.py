from pathlib import Path

from django.apps import AppConfig


class HamroGymConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nepanest.products.hamrogym"
    label = "hamrogym"
    path = str(Path(__file__).resolve().parent)

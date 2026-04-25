from pathlib import Path

from django.apps import AppConfig


class TaskModuleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nepanest.modules.tasks"
    label = "task"
    path = str(Path(__file__).resolve().parent)

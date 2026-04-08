from django.apps import AppConfig


class TaskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Apps.task"
    label = "task"

    # def ready(self):
    #     import Apps.task.signals
from django.db import models
from nepanest.common.mixins import ERPBaseModel

class TaskModule(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        app_label = "task"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

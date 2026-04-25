from django.db import models

from nepanest.common.mixins import ERPBaseModel


class TaskType(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    sequence = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        app_label = "task"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

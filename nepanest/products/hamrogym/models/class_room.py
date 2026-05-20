from django.db import models
from core.mixins.erp import ERPBaseModel

class ClassRoom(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

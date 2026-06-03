from django.db import models
from core.mixins.erp import ERPBaseModel

class ServiceType(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

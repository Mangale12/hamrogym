from django.db import models
from core.mixins.erp import ERPBaseModel

class Service(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    service_type = models.ForeignKey("ServiceType", on_delete=models.SET_NULL, null=True, blank=True)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

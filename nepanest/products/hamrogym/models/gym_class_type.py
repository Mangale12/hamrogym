from django.db import models
from core.mixins.erp import ERPBaseModel


class GymClassType(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        db_table = "gym_class_type"


    def __str__(self) -> str:
        return self.name

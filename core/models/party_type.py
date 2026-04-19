from django.db import models

from core.mixins import ERPBaseModel


class PartyType(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

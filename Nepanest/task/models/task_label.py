from django.db import models
from core.mixins import ERPBaseModel
from core.choices import BADGE_COLOR_CHOICES
class TaskLabel(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True, choices=BADGE_COLOR_CHOICES)
    sequence = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

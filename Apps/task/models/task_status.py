from django.db import models

from core.choices import BADGE_COLOR_CHOICES
from core.mixins import ERPBaseModel


class TaskStatus(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    badge_color = models.CharField(max_length=20, choices=BADGE_COLOR_CHOICES, blank=True, null=True)
    sequence = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

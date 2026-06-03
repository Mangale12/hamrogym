from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from core.mixins.erp import ActiveRemarksModelMixin, TimeStampedModelMixin


hex_color_validator = RegexValidator(
    regex=r"^#(?:[0-9A-Fa-f]{6})$",
    message="Enter a valid hex color code like #3498DB.",
)


class LeadStatus(ActiveRemarksModelMixin, TimeStampedModelMixin):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    sequence = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)
    color = models.CharField(
        max_length=7,
        default="#3498DB",
        validators=[hex_color_validator],
    )
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ["sequence", "name", "id"]

    def __str__(self) -> str:
        return self.name

    def clean(self):
        errors = {}

        if self.is_default:
            queryset = type(self).objects.filter(is_default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                errors["is_default"] = "Only one lead status can be marked as default."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.name = (self.name or "").strip()
        self.code = (self.code or "").strip().lower()
        self.color = (self.color or "#3498DB").strip().upper()
        self.full_clean()
        return super().save(*args, **kwargs)

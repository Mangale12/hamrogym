from django.db import models

from .location_type import LocationType


class Location(models.Model):
    location_type = models.ForeignKey(
        LocationType,
        on_delete=models.CASCADE,
        related_name="locations",
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        unique_together = ("location_type", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.location_type})"

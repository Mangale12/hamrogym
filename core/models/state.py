from django.db import models

from .country import Country


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="states")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        unique_together = ("country", "name")

    def __str__(self):
        return f"{self.name} ({self.country})"

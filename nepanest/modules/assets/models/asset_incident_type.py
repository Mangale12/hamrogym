from django.db import models


class AssetIncidentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True)
    require_approval = models.BooleanField(default=False)
    auto_create_maintenance = models.BooleanField(default=False)
    financial_impact = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "assets"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

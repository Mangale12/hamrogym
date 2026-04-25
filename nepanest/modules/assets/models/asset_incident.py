from django.conf import settings
from django.db import models
from core.choices import ASSET_INCIDENT_STATUS_CHOICES as STATUS_CHOICES


class AssetIncident(models.Model):
    asset = models.ForeignKey("Asset", on_delete=models.RESTRICT, related_name="incidents")
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="asset_incidents",
        null=True,
        blank=True,
    )
    incident_type = models.ForeignKey("AssetIncidentType", on_delete=models.RESTRICT, related_name="asset_incidents")
    incident_date = models.DateField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    approval_deduction_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reported_asset_incidents",
        null=True,
        blank=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_asset_incidents",
        null=True,
        blank=True,
    )
    fiscal_year = models.ForeignKey("core.FiscalYear", on_delete=models.RESTRICT, related_name="asset_incidents")
    branch = models.ForeignKey("core.Branch", on_delete=models.RESTRICT, related_name="asset_incidents")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "assets"
        ordering = ["-incident_date", "-id"]

    def __str__(self) -> str:
        return f"{self.asset} - {self.incident_type} ({self.incident_date})"

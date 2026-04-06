from django.conf import settings
from django.db import models


class AssetMaintenanceRecord(models.Model):
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
    ]

    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )
    incident = models.OneToOneField(
        "AssetIncident",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_record",
    )
    maintenance_date = models.DateField()
    maintenance_type = models.CharField(max_length=100)
    vendor = models.ForeignKey(
        "AssetVendor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_records",
    )
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_maintenance_performed",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-maintenance_date", "-id"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from ..services import sync_asset_state

        sync_asset_state(self.asset)

    def delete(self, *args, **kwargs):
        asset = self.asset
        super().delete(*args, **kwargs)
        from ..services import sync_asset_state

        sync_asset_state(asset)

    def __str__(self) -> str:
        return f"{self.asset} - {self.maintenance_type}"

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AssetTransfer(models.Model):
    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="transfers",
    )
    transfer_date = models.DateField()
    from_location = models.ForeignKey(
        "core.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_transfers_from",
    )
    to_location = models.ForeignKey(
        "core.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_transfers_to",
    )
    from_department = models.ForeignKey(
        "hr.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_transfers_from",
    )
    to_department = models.ForeignKey(
        "hr.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_transfers_to",
    )
    transferred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_transfers_created",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_transfers_received",
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-transfer_date", "-id"]

    def clean(self):
        errors = {}
        if not self.to_location_id and not self.to_department_id:
            errors["to_location"] = "Transfer needs a destination location or department."
            errors["to_department"] = "Transfer needs a destination location or department."
        if self.from_location_id and self.to_location_id and self.from_location_id == self.to_location_id:
            errors["to_location"] = "Destination location must be different from source location."
        if self.from_department_id and self.to_department_id and self.from_department_id == self.to_department_id:
            errors["to_department"] = "Destination department must be different from source department."
        if errors:
            raise ValidationError(errors)

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
        return f"{self.asset} transfer on {self.transfer_date}"

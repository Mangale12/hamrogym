from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AssetAssignment(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_RETURNED = "returned"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_RETURNED, "Returned"),
    ]

    asset = models.ForeignKey("Asset", on_delete=models.CASCADE, related_name="assignments")
    employee = models.ForeignKey("hr.Employee", on_delete=models.CASCADE, related_name="asset_assignments")
    assigned_date = models.DateField()
    expected_return_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_assignments_created",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_assignments_received",
    )
    condition_at_issue = models.ForeignKey(
        "AssetCondition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_asset_assignments",
    )
    condition_at_return = models.ForeignKey(
        "AssetCondition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="returned_asset_assignments",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-assigned_date", "-id"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from ..services import sync_asset_state

        sync_asset_state(self.asset)

    def delete(self, *args, **kwargs):
        asset = self.asset
        super().delete(*args, **kwargs)
        from ..services import sync_asset_state

        sync_asset_state(asset)

    def clean(self):
        errors = {}
        if self.expected_return_date and self.assigned_date and self.expected_return_date < self.assigned_date:
            errors["expected_return_date"] = "Expected return date cannot be earlier than assigned date."
        if self.return_date and self.assigned_date and self.return_date < self.assigned_date:
            errors["return_date"] = "Return date cannot be earlier than assigned date."
        if self.status == self.STATUS_ACTIVE and self.return_date:
            errors["status"] = "Active assignments cannot have a return date."
        if self.status == self.STATUS_RETURNED and not self.return_date:
            errors["return_date"] = "Return date is required when assignment is returned."
        if self.status == self.STATUS_RETURNED and not self.received_by_id:
            errors["received_by"] = "Received by is required when assignment is returned."
        if self.status == self.STATUS_RETURNED and not self.condition_at_return_id:
            errors["condition_at_return"] = "Condition at return is required when assignment is returned."
        if self.asset_id and self.status == self.STATUS_ACTIVE:
            existing = AssetAssignment.objects.filter(asset_id=self.asset_id, status=self.STATUS_ACTIVE)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                errors["asset"] = "This asset already has an active assignment."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.asset} -> {self.employee} ({self.status})"

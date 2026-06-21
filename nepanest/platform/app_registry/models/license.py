from django.db import models

class License(models.Model):
    """
    Tracks what features/limits a client is licensed for.
    Only one license should be current (is_current=True) per client at a time.
    """

    class Plan(models.TextChoices):
        STARTER = "starter", "Starter"
        PROFESSIONAL = "professional", "Professional"
        ENTERPRISE = "enterprise", "Enterprise"

    client = models.ForeignKey(
        "app_registry.Client",
        on_delete=models.CASCADE,
        related_name="licenses",
    )
    plan = models.CharField(max_length=30, choices=Plan.choices)
    issued_on = models.DateField()
    expires_on = models.DateField()
    max_users = models.PositiveIntegerField(default=5)
    max_branches = models.PositiveIntegerField(default=1)
    grace_days = models.PositiveIntegerField(default=7)
    is_current = models.BooleanField(default=True)

    class Meta:
        ordering = ["-issued_on"]
        verbose_name = "License"
        verbose_name_plural = "Licenses"

    def __str__(self):
        return f"{self.client} — {self.plan} (expires {self.expires_on})"

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expires_on < timezone.now().date()


class LicenseRenewHistory(models.Model):
    """
    Records noteworthy changes made to a license over time.
    """

    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        RENEWED = "renewed", "Renewed"
        SUSPENDED = "suspended", "Suspended"
        REACTIVATED = "reactivated", "Reactivated"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    license = models.ForeignKey(
        "app_registry.License",
        on_delete=models.CASCADE,
        related_name="history_entries",
    )
    old_expiry = models.DateTimeField(null=True, blank=True)
    new_expiry = models.DateTimeField(null=True, blank=True)
    renewed_by = models.CharField(max_length=255, blank=True)
    renewed_at = models.DateTimeField(null=True, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices, default=Action.UPDATED)
    notes = models.TextField(blank=True, db_column="remarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "License Renew History"
        verbose_name_plural = "License Renew Histories"
        db_table = "app_registry_license_history"

    def __str__(self):
        if self.created_at:
            return f"{self.license} — {self.get_action_display()} @ {self.created_at:%Y-%m-%d %H:%M}"
        return f"{self.license} — {self.get_action_display()}"

    @property
    def remarks(self):
        return self.notes

    @remarks.setter
    def remarks(self, value):
        self.notes = value


# Backward-compatible alias used throughout the app.
LicenseHistory = LicenseRenewHistory

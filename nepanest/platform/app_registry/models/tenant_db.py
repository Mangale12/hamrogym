from django.db import models


class TenantDB(models.Model):
    """
    Stores per-client database credentials and lifecycle status.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        EXPIRED = "expired", "Expired"
        TRIAL = "trial", "Trial"

    client = models.ForeignKey(
        "app_registry.Client",
        on_delete=models.CASCADE,
        related_name="tenant_dbs",
    )
    code = models.CharField(max_length=50, unique=True)  # e.g. "gym_code"
    db_name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    db_user = models.CharField(max_length=100)
    db_password = models.CharField(max_length=200)
    db_host = models.CharField(max_length=200, default="127.0.0.1")
    db_port = models.CharField(max_length=10, default="3306")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIAL)

    class Meta:
        ordering = ["db_name"]
        verbose_name = "Tenant DB"
        verbose_name_plural = "Tenant DBs"
        db_table = "app_registry_tenant_dbs"

    def __str__(self):
        return f"{self.client} — {self.db_name}"

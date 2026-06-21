from django.db import models


class Client(models.Model):
    """
    Represents a business/organization that has purchased nepanest.
    This is the top-level entity in the registry — everything else hangs off it.
    """

    class Plan(models.TextChoices):
        STARTER = "starter", "Starter"
        PROFESSIONAL = "professional", "Professional"
        ENTERPRISE = "enterprise", "Enterprise"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        CANCELLED = "cancelled", "Cancelled"
        TRIAL = "trial", "Trial"

    business_name = models.CharField(max_length=255)
    client_code = models.CharField(max_length=50, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    plan = models.CharField(max_length=30, choices=Plan.choices, default=Plan.STARTER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIAL)
    registered_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-registered_on"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.business_name} ({self.client_code})"


class ClientContact(models.Model):
    """
    Represents a contact person for a client.
    """

    client = models.ForeignKey(
        "app_registry.Client",
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.email})"
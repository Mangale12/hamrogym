from django.conf import settings
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="core_organizations_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class OrganizationSettings(models.Model):
    CALENDAR_CHOICES = [
        ("AD", "AD"),
        ("BS", "BS"),
    ]

    name = models.CharField(
        max_length=25,
        unique=True,
        null=True,
        blank=True,
        help_text="Name of the organization",
    )
    registration_number = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Registration number of the organization",
    )
    pan_vat_number = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="PAN/VAT number of the organization",
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Phone number of the organization",
    )
    email = models.EmailField(null=True, blank=True, help_text="Email address of the organization")
    website = models.URLField(null=True, blank=True, help_text="Website URL of the organization")
    logo = models.ImageField(
        upload_to="organization_logos/",
        null=True,
        blank=True,
        help_text="Logo of the organization",
    )
    address = models.TextField(null=True, blank=True, help_text="Address of the organization")
    contact_person = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name of the contact person",
    )
    calendar = models.CharField(
        max_length=2,
        choices=CALENDAR_CHOICES,
        null=True,
        blank=True,
        help_text="Calendar type",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"

    def __str__(self):
        return self.name


class Branch(models.Model):
    organization = models.ForeignKey("core.Organization", on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="core_branches_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        ordering = ["organization__name", "name"]
        unique_together = ("organization", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.organization})"


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ErpEntity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    module = models.CharField(max_length=255, blank=True)
    app_label = models.CharField(max_length=255, blank=True)
    model_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "erp_entity"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

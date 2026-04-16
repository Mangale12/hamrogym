from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.mixins.erp import ERPBaseModel


class BillingProfile(ERPBaseModel):
    BILLING_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("vendor", "Vendor"),
        ("internal", "Internal"),
        ("partner", "Partner"),
    )

    # Basic Info
    name = models.CharField(max_length=255)
    billing_type = models.CharField(max_length=20, choices=BILLING_TYPE_CHOICES)
    # Generic Relation (Customer / Vendor / Department / Company)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    related_object = GenericForeignKey("content_type", "object_id")
    # Financial Info
    tax_number = models.CharField(max_length=100, null=True, blank=True)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    currency = models.ForeignKey("core.Currency", on_delete=models.PROTECT, related_name="billing_profiles")
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        ordering = ["name"]

    @property
    def related_object_label(self):
        return str(self.related_object) if self.related_object else ""

    def __str__(self):
        return f"{self.name} ({self.billing_type})"

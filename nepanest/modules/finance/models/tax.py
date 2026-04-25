from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
import core
from nepanest.foundation.geography import Country
from nepanest.foundation.parties import PartyType


ZERO = Decimal("0")
HUNDRED = Decimal("100")


class ApplicationScope(models.TextChoices):
    SALES = "sales", "Sales"
    PURCHASE = "purchase", "Purchase"
    BOTH = "both", "Both"


class TaxType(models.TextChoices):
    VAT = "vat", "VAT"
    GST = "gst", "GST"
    SERVICE = "service", "Service Tax"
    WITHHOLDING = "withholding", "Withholding Tax"
    EXCISE = "excise", "Excise"
    CUSTOM = "custom", "Custom"


class TaxCalculationMethod(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    FIXED = "fixed", "Fixed Amount"


class TaxRuleType(models.TextChoices):
    LINE_NET = "line_net", "Line Net"
    DOCUMENT_NET = "document_net", "Document Net"
    SHIPPING = "shipping", "Shipping"
    ACTUAL = "actual", "Actual Amount"


APPLICATION_SCOPE_CHOICES = ApplicationScope.choices
TAX_TYPE_CHOICES = TaxType.choices
TAX_CALCULATION_METHOD_CHOICES = TaxCalculationMethod.choices
TAX_RULE_TYPE_CHOICES = TaxRuleType.choices


def scopes_are_compatible(left_scope: str, right_scope: str) -> bool:
    return (
        left_scope in {ApplicationScope.BOTH, right_scope}
        or right_scope in {ApplicationScope.BOTH, left_scope}
    )


class TaxTrackedModel(models.Model):
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TaxNamedModel(TaxTrackedModel):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Tax(TaxNamedModel):
    tax_type = models.CharField(max_length=30, choices=TaxType.choices, default=TaxType.VAT)
    calculation_method = models.CharField(
        max_length=20,
        choices=TaxCalculationMethod.choices,
        default=TaxCalculationMethod.PERCENTAGE,
    )
    application_scope = models.CharField(
        max_length=20,
        choices=ApplicationScope.choices,
        default=ApplicationScope.BOTH,
    )
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=ZERO)
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=ZERO)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    is_inclusive = models.BooleanField(default=False)
    is_recoverable = models.BooleanField(default=True)

    class Meta:
        app_label = "finance"
        ordering = ["name", "id"]

    @property
    def amount_value(self) -> Decimal:
        if self.calculation_method == TaxCalculationMethod.FIXED:
            return self.fixed_amount or ZERO
        return self.rate or ZERO

    def clean(self):
        errors = {}
        rate = self.rate if self.rate is not None else ZERO
        fixed_amount = self.fixed_amount if self.fixed_amount is not None else ZERO

        if self.calculation_method == TaxCalculationMethod.PERCENTAGE:
            if rate < ZERO or rate > HUNDRED:
                errors["rate"] = "Rate must be between 0 and 100 for percentage taxes."
            if fixed_amount != ZERO:
                errors["fixed_amount"] = "Fixed amount must be 0 for percentage taxes."
        else:
            if fixed_amount <= ZERO:
                errors["fixed_amount"] = "Fixed amount must be greater than 0 for fixed taxes."
            if rate != ZERO:
                errors["rate"] = "Rate must be 0 for fixed taxes."

        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            errors["effective_to"] = "Effective to date cannot be earlier than effective from date."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class TaxGroup(TaxNamedModel):
    application_scope = models.CharField(
        max_length=20,
        choices=ApplicationScope.choices,
        default=ApplicationScope.BOTH,
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        app_label = "finance"
        ordering = ["name", "id"]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class TaxGroupItem(TaxTrackedModel):
    tax_group = models.ForeignKey(TaxGroup, on_delete=models.CASCADE, related_name="items")
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, related_name="tax_group_items")
    sequence = models.PositiveIntegerField(default=1)
    override_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_compound = models.BooleanField(default=False)

    class Meta:
        app_label = "finance"
        ordering = ["sequence", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["tax_group", "tax"],
                name="unique_tax_group_item_tax",
            ),
        ]

    def clean(self):
        errors = {}

        if self.override_rate is not None and (self.override_rate < ZERO or self.override_rate > HUNDRED):
            errors["override_rate"] = "Override rate must be between 0 and 100."

        if (
            self.tax_id
            and self.tax_group_id
            and not scopes_are_compatible(self.tax.application_scope, self.tax_group.application_scope)
        ):
            errors["tax"] = "Tax scope must match the selected tax group scope."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.tax_group} - {self.tax}"


class TaxRule(TaxNamedModel):
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, related_name="rules")
    rule_type = models.CharField(
        max_length=20,
        choices=TaxRuleType.choices,
        default=TaxRuleType.LINE_NET,
    )
    application_scope = models.CharField(
        max_length=20,
        choices=ApplicationScope.choices,
        default=ApplicationScope.BOTH,
    )
    party_type = models.ForeignKey(PartyType, on_delete=models.PROTECT, related_name="tax_rules", null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="tax_rules", null=True, blank=True)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    priority = models.PositiveIntegerField(default=1)
    stop_processing = models.BooleanField(default=False)

    class Meta:
        app_label = "finance"
        ordering = ["priority", "name", "id"]

    def clean(self):
        errors = {}

        if self.min_amount is not None and self.min_amount < ZERO:
            errors["min_amount"] = "Min amount cannot be negative."

        if self.max_amount is not None and self.max_amount < ZERO:
            errors["max_amount"] = "Max amount cannot be negative."

        if self.max_amount is not None and self.min_amount is not None and self.max_amount < self.min_amount:
            errors["max_amount"] = "Max amount cannot be less than min amount."

        if self.tax_id and not scopes_are_compatible(self.tax.application_scope, self.application_scope):
            errors["application_scope"] = "Rule scope must be compatible with the selected tax scope."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

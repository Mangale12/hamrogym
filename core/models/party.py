from django.db import models

from core.mixins import ERPBaseModel

from .party_type import PartyType


class Party(ERPBaseModel):
    PARTY_CATEGORY = (
        ("individual", "Individual"),
        ("company", "Company"),
    )

    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    party_type = models.ForeignKey(
        PartyType,
        on_delete=models.PROTECT,
        related_name="parties",
    )
    category = models.CharField(max_length=20, choices=PARTY_CATEGORY)
    pan_number = models.CharField(max_length=50, blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self) -> str:
        return self.display_name or self.name


class PartyContact(ERPBaseModel):
    CONTACT_TYPE = (
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("billing", "Billing"),
        ("support", "Support"),
    )

    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="contacts")
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=20, choices=CONTACT_TYPE)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["party_id", "id"]

    def __str__(self) -> str:
        return self.contact_person or self.email or self.phone or f"Contact #{self.pk}"


class PartyAddress(ERPBaseModel):
    ADDRESS_TYPE = (
        ("billing", "Billing"),
        ("shipping", "Shipping"),
        ("office", "Office"),
        ("home", "Home"),
    )

    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="addresses")
    type = models.CharField(max_length=20, choices=ADDRESS_TYPE)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["party_id", "id"]

    def __str__(self) -> str:
        return self.address or self.city or f"Address #{self.pk}"


class PartyFinancial(ERPBaseModel):
    BALANCE_TYPE_CHOICES = (
        ("dr", "Debit"),
        ("cr", "Credit"),
    )

    party = models.OneToOneField(Party, on_delete=models.CASCADE, related_name="financial")
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_type = models.CharField(max_length=10, choices=BALANCE_TYPE_CHOICES, default="dr")
    payment_terms = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self) -> str:
        return f"Financials for {self.party}"


class PartyBankDetail(ERPBaseModel):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="bank_details")
    bank_name = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=100)
    branch = models.CharField(max_length=255, blank=True, null=True)
    ifsc_swift_code = models.CharField(max_length=50, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["party_id", "id"]

    def __str__(self) -> str:
        return f"{self.bank_name} - {self.account_number}"

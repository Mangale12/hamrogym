from django.db import models
from nepanest.common.mixins.erp import ERPBaseModel

class BillingDocument(ERPBaseModel):
    DOCUMENT_TYPE_CHOICES = (
        ("invoice", "Invoice"),        # customer
        ("bill", "Bill"),              # vendor
        ("credit_note", "Credit Note"),
        ("debit_note", "Debit Note"),
        ("proforma", "Proforma"),
    )

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("partially_paid", "Partially Paid"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
        ("overdue", "Overdue"),
    )

    SOURCE_TYPE_CHOICES = (
        ("task", "Task"),
        ("sales", "Sales"),
        ("purchase", "Purchase"),
        ("manual", "Manual"),
        ("subscription", "Subscription"),
    )

    # 🔥 BASIC INFO
    document_number = models.CharField(max_length=100, unique=True)
    billing_profile = models.ForeignKey(
        "billing.BillingProfile",
        on_delete=models.PROTECT,
        related_name="documents"
    )

    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    # 🔥 SOURCE LINK (ENTITY DRIVEN)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default="manual")
    source_id = models.PositiveBigIntegerField(null=True, blank=True)

    # 🔥 DATES
    document_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    posting_date = models.DateField(null=True, blank=True)

    # 🔥 AMOUNTS
    subtotal_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # 🔥 CURRENCY
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT
    )
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1)

    terms_conditions = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "billing"

    def __str__(self):
        return self.document_number
    
    
    


class BillingItem(ERPBaseModel):
    SOURCE_TYPE_CHOICES = (
        ("product", "Product"),
        ("service", "Service"),
        ("task_log", "Task Log"),
        ("expense", "Expense"),
        ("manual", "Manual"),
    )

    billing_document = models.ForeignKey(
        "billing.BillingDocument",
        on_delete=models.CASCADE,
        related_name="items"
    )

    # 🔥 Source Linking (Entity Driven)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default="manual")
    source_id = models.PositiveBigIntegerField(null=True, blank=True)

    # 🔥 Item Info
    name = models.CharField(max_length=255)

    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # 🔥 Discount
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # 🔥 Tax
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # 🔥 Totals
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        app_label = "billing"

    def __str__(self):
        return self.name

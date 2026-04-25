from django.conf import settings
from django.db import models


class AssetDepreciationRegister(models.Model):
    STATUS_UNPOSTED = "unposted"
    STATUS_POSTED = "posted"
    STATUS_CHOICES = [
        (STATUS_UNPOSTED, "Unposted"),
        (STATUS_POSTED, "Posted"),
    ]

    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.CASCADE,
        related_name="depreciation_register_entries",
    )
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="asset_depreciation_register_entries",
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="asset_depreciation_register_entries",
    )
    fiscal_year = models.ForeignKey(
        "core.FiscalYear",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="asset_depreciation_register_entries",
    )
    schedule_month = models.DateField()
    period_start = models.DateField()
    period_end = models.DateField()
    method = models.CharField(max_length=30, default="straight_line")
    life_month_index = models.PositiveIntegerField(default=1)
    useful_life_months = models.PositiveIntegerField(default=1)
    purchase_cost = models.DecimalField(max_digits=14, decimal_places=2, default="0.00")
    salvage_value = models.DecimalField(max_digits=14, decimal_places=2, default="0.00")
    depreciable_amount = models.DecimalField(max_digits=14, decimal_places=2, default="0.00")
    depreciation_amount = models.DecimalField(max_digits=14, decimal_places=2, default="0.00")
    opening_book_value = models.DecimalField(max_digits=14, decimal_places=2, default="0.00")
    closing_book_value = models.DecimalField(max_digits=14, decimal_places=2, default="0.00")
    fixed_asset_account = models.ForeignKey(
        "account.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="asset_depreciation_fixed_asset_entries",
    )
    depreciation_expense_account = models.ForeignKey(
        "account.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="asset_depreciation_expense_entries",
    )
    accumulated_depreciation_account = models.ForeignKey(
        "account.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="asset_depreciation_accumulated_entries",
    )
    journal_entry = models.ForeignKey(
        "account.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_depreciation_entries",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNPOSTED)
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_depreciation_posted_entries",
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "assets"
        ordering = ["-schedule_month", "asset__name", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "schedule_month", "branch"],
                name="unique_asset_depreciation_register_asset_month_branch",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.asset} - {self.schedule_month:%Y-%m}"

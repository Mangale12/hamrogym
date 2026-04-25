from django.db import models


class AssetCategory(models.Model):
    DEPRECIATION_METHOD_STRAIGHT_LINE = "straight_line"
    DEPRECIATION_METHOD_CHOICES = [
        (DEPRECIATION_METHOD_STRAIGHT_LINE, "Straight Line"),
    ]

    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="subcategories")
    depreciation_applicable = models.BooleanField(default=False)
    depreciation_method = models.CharField(
        max_length=30,
        choices=DEPRECIATION_METHOD_CHOICES,
        default=DEPRECIATION_METHOD_STRAIGHT_LINE,
    )
    default_useful_life_months = models.PositiveIntegerField(null=True, blank=True)
    fixed_asset_account = models.ForeignKey(
        "account.ChartOfAccount",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="asset_category_fixed_asset_accounts",
    )
    depreciation_expense_account = models.ForeignKey(
        "account.ChartOfAccount",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="asset_category_depreciation_expense_accounts",
    )
    accumulated_depreciation_account = models.ForeignKey(
        "account.ChartOfAccount",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="asset_category_accumulated_depreciation_accounts",
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "assets"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

ACCOUNT_TYPE_CHOICES = [
    ("asset", "Asset"),
    ("liability", "Liability"),
    ("equity", "Equity"),
    ("income", "Income"),
    ("expense", "Expense"),
]

REPORT_TYPE_CHOICES = [
    ("balance_sheet", "Balance Sheet"),
    ("profit_loss", "Profit & Loss"),
]

REPORT_TYPE_BY_ACCOUNT_TYPE = {
    "asset": "balance_sheet",
    "liability": "balance_sheet",
    "equity": "balance_sheet",
    "income": "profit_loss",
    "expense": "profit_loss",
}

ROOT_CODE_STARTS = {
    "asset": 1000,
    "liability": 2000,
    "equity": 3000,
    "income": 4000,
    "expense": 5000,
}


class ChartOfAccount(models.Model):
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="account_chart_of_accounts",
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="account_chart_of_accounts",
    )
    fiscal_year = models.ForeignKey(
        "core.FiscalYear",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="account_chart_of_accounts",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=30, unique=True, blank=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, editable=False)
    report_level = models.PositiveIntegerField(default=1, editable=False)
    is_ledger = models.BooleanField(default=False)
    allow_direct_posting = models.BooleanField(default=True)
    is_depreciation = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_chart_of_accounts_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_chart_of_accounts_updated",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name", "branch"],
                name="unique_chart_of_account_name_per_parent_branch",
            ),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._capture_original_state()

    def __str__(self) -> str:
        if self.code:
            return f"{self.code} - {self.name}"
        return self.name

    @property
    def indented_name(self) -> str:
        prefix = "  " * max(self.report_level - 1, 0)
        return f"{prefix}{self.name}"

    @property
    def full_path(self) -> str:
        parts = [self.name]
        parent = self.parent
        while parent:
            parts.append(parent.name)
            parent = parent.parent
        return " > ".join(reversed(parts))

    def clean(self):
        errors = {}
        self.report_type = REPORT_TYPE_BY_ACCOUNT_TYPE.get(self.account_type, "balance_sheet")
        self.report_level = (self.parent.report_level + 1) if self.parent_id and self.parent else 1
        self.allow_direct_posting = bool(self.is_ledger)

        if self.parent_id and self.pk and self.parent_id == self.pk:
            errors["parent"] = "An account head cannot be its own parent."

        ancestor = self.parent
        while ancestor:
            if self.pk and ancestor.pk == self.pk:
                errors["parent"] = "Circular parent relationships are not allowed."
                break
            ancestor = ancestor.parent

        if self.parent and self.parent.account_type != self.account_type:
            errors["account_type"] = "Child account heads must use the same account type as the parent."

        if self.parent and self.parent.is_ledger:
            errors["parent"] = "Ledger accounts cannot be used as parent heads."

        if self.is_ledger and self.pk and self.children.exists():
            errors["is_ledger"] = "A ledger account cannot have child chart heads."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.report_type = REPORT_TYPE_BY_ACCOUNT_TYPE.get(self.account_type, "balance_sheet")
        self.report_level = (self.parent.report_level + 1) if self.parent_id and self.parent else 1
        self.allow_direct_posting = bool(self.is_ledger)

        parent_changed = self.pk and self.parent_id != self._original_parent_id
        code_missing = not (self.code or "").strip()

        if code_missing or parent_changed:
            self.code = self._generate_next_code()

        self.full_clean()

        structure_changed = (
            parent_changed
            or self.code != self._original_code
            or self.report_level != self._original_report_level
            or self.account_type != self._original_account_type
        )

        super().save(*args, **kwargs)

        if structure_changed:
            self._sync_descendants()

        self._capture_original_state()

    def delete(self, *args, **kwargs):
        children = list(self.children.all().order_by("sort_order", "id"))
        parent = self.parent
        with transaction.atomic():
            super().delete(*args, **kwargs)
            for child in children:
                child.parent = parent
                child.save()

    def _capture_original_state(self):
        self._original_parent_id = self.parent_id
        self._original_code = self.code
        self._original_report_level = self.report_level
        self._original_account_type = self.account_type

    def _generate_next_code(self) -> str:
        queryset = self.__class__.objects.exclude(pk=self.pk)

        if self.parent_id and self.parent:
            return self._generate_child_code(queryset)

        base_code = ROOT_CODE_STARTS.get(self.account_type, 9000)
        sibling_codes = queryset.filter(parent__isnull=True, account_type=self.account_type).values_list(
            "code",
            flat=True,
        )
        used_codes = set()
        for sibling_code in sibling_codes:
            sibling_code = str(sibling_code or "")
            if sibling_code[:4].isdigit():
                used_codes.add(int(sibling_code[:4]))

        next_code = base_code
        while next_code in used_codes:
            next_code += 100
        return f"{next_code:04d}"

    def _generate_child_code(self, queryset) -> str:
        sibling_codes = queryset.filter(parent=self.parent).values_list("code", flat=True)
        parent_code = str(self.parent.code or "")

        if self.parent.report_level == 1 and parent_code.isdigit():
            next_code = int(parent_code) + 100
            used_codes = {
                int(str(code))
                for code in sibling_codes
                if str(code or "").isdigit()
            }
            while next_code in used_codes:
                next_code += 100
            return f"{next_code:04d}"

        next_segment = 1
        for sibling_code in sibling_codes:
            sibling_code = str(sibling_code or "")
            if not sibling_code.startswith(parent_code):
                continue
            suffix = sibling_code[len(parent_code) : len(parent_code) + 2]
            if suffix.isdigit():
                next_segment = max(next_segment, int(suffix) + 1)
        return f"{parent_code}{next_segment:02d}"

    def _sync_descendants(self):
        children = list(self.children.all().order_by("sort_order", "id"))
        for index, child in enumerate(children, start=1):
            child.account_type = self.account_type
            child.report_type = self.report_type
            child.report_level = self.report_level + 1
            child.is_ledger = bool(child.is_ledger)
            if self.report_level == 1 and str(self.code or "").isdigit():
                child.code = f"{int(self.code) + (index * 100):04d}"
            else:
                child.code = f"{self.code}{index:02d}"
            child.save()


class Ledger(models.Model):
    chart_account = models.OneToOneField(
        ChartOfAccount,
        on_delete=models.CASCADE,
        related_name="ledger_profile",
    )
    pan_no = models.CharField(max_length=50, blank=True)
    vat_no = models.CharField(max_length=50, blank=True)
    contact_person = models.CharField(max_length=150, blank=True)
    mobile_no = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["chart_account__code", "id"]

    def __str__(self) -> str:
        return str(self.chart_account)

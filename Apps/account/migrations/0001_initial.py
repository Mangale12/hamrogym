# Generated manually on 2026-04-14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


SEED_CHART = [
    {
        "code": "1000",
        "name": "Assets",
        "account_type": "asset",
        "report_type": "balance_sheet",
        "allow_direct_posting": False,
        "children": [
            {
                "code": "1100",
                "name": "Current Assets",
                "children": [
                    {"code": "110001", "name": "Cash in Hand"},
                    {"code": "110002", "name": "Cash at Bank"},
                    {"code": "110003", "name": "Petty Cash"},
                    {"code": "110004", "name": "Accounts Receivable"},
                    {"code": "110005", "name": "Employee Receivable"},
                    {"code": "110006", "name": "Advance to Supplier"},
                    {"code": "110007", "name": "Inventory"},
                    {"code": "110008", "name": "Prepaid Expenses"},
                    {"code": "110009", "name": "Input VAT / Tax Receivable"},
                ],
            },
            {
                "code": "1200",
                "name": "Non Current Assets",
                "children": [
                    {"code": "120001", "name": "Land"},
                    {"code": "120002", "name": "Building"},
                    {"code": "120003", "name": "Furniture and Fixtures"},
                    {"code": "120004", "name": "Office Equipment"},
                    {"code": "120005", "name": "Computer Equipment"},
                    {"code": "120006", "name": "Gym Equipment"},
                    {"code": "120007", "name": "Vehicles"},
                    {"code": "120008", "name": "Leasehold Improvements"},
                    {"code": "120009", "name": "Security Deposits"},
                ],
            },
            {
                "code": "1300",
                "name": "Accumulated Depreciation",
                "children": [
                    {"code": "130001", "name": "Accumulated Depreciation - Building", "is_depreciation": True},
                    {"code": "130002", "name": "Accumulated Depreciation - Furniture and Fixtures", "is_depreciation": True},
                    {"code": "130003", "name": "Accumulated Depreciation - Office Equipment", "is_depreciation": True},
                    {"code": "130004", "name": "Accumulated Depreciation - Computer Equipment", "is_depreciation": True},
                    {"code": "130005", "name": "Accumulated Depreciation - Gym Equipment", "is_depreciation": True},
                    {"code": "130006", "name": "Accumulated Depreciation - Vehicles", "is_depreciation": True},
                ],
            },
        ],
    },
    {
        "code": "2000",
        "name": "Liabilities",
        "account_type": "liability",
        "report_type": "balance_sheet",
        "allow_direct_posting": False,
        "children": [
            {
                "code": "2100",
                "name": "Current Liabilities",
                "children": [
                    {"code": "210001", "name": "Accounts Payable"},
                    {"code": "210002", "name": "Salary Payable"},
                    {"code": "210003", "name": "Tax Payable"},
                    {"code": "210004", "name": "VAT Payable"},
                    {"code": "210005", "name": "SSF Payable"},
                    {"code": "210006", "name": "Accrued Expenses"},
                    {"code": "210007", "name": "Unearned Revenue"},
                    {"code": "210008", "name": "Short Term Loan"},
                ],
            },
            {
                "code": "2200",
                "name": "Non Current Liabilities",
                "children": [
                    {"code": "220001", "name": "Long Term Loan"},
                    {"code": "220002", "name": "Bank Loan"},
                    {"code": "220003", "name": "Lease Liability"},
                ],
            },
        ],
    },
    {
        "code": "3000",
        "name": "Equity",
        "account_type": "equity",
        "report_type": "balance_sheet",
        "allow_direct_posting": False,
        "children": [
            {
                "code": "3100",
                "name": "Capital",
                "children": [
                    {"code": "310001", "name": "Owner Capital"},
                    {"code": "310002", "name": "Partner Capital"},
                ],
            },
            {
                "code": "3200",
                "name": "Reserves and Earnings",
                "children": [
                    {"code": "320001", "name": "Retained Earnings"},
                    {"code": "320002", "name": "Current Year Earnings"},
                ],
            },
            {
                "code": "3300",
                "name": "Drawings",
                "children": [
                    {"code": "330001", "name": "Owner Drawings"},
                ],
            },
        ],
    },
    {
        "code": "4000",
        "name": "Income",
        "account_type": "income",
        "report_type": "profit_loss",
        "allow_direct_posting": False,
        "children": [
            {
                "code": "4100",
                "name": "Operating Revenue",
                "children": [
                    {"code": "410001", "name": "Membership Revenue"},
                    {"code": "410002", "name": "Personal Training Revenue"},
                    {"code": "410003", "name": "Admission Fee Revenue"},
                    {"code": "410004", "name": "Locker Revenue"},
                    {"code": "410005", "name": "Group Class Revenue"},
                    {"code": "410006", "name": "Supplement Sales Revenue"},
                    {"code": "410007", "name": "Other Service Revenue"},
                ],
            },
            {
                "code": "4200",
                "name": "Other Income",
                "children": [
                    {"code": "420001", "name": "Interest Income"},
                    {"code": "420002", "name": "Gain on Asset Disposal"},
                    {"code": "420003", "name": "Miscellaneous Income"},
                ],
            },
        ],
    },
    {
        "code": "5000",
        "name": "Expenses",
        "account_type": "expense",
        "report_type": "profit_loss",
        "allow_direct_posting": False,
        "children": [
            {
                "code": "5100",
                "name": "Cost of Sales",
                "children": [
                    {"code": "510001", "name": "Supplement Purchase"},
                    {"code": "510002", "name": "Merchandise Purchase"},
                    {"code": "510003", "name": "Direct Service Cost"},
                ],
            },
            {
                "code": "5200",
                "name": "Operating Expenses",
                "children": [
                    {"code": "520001", "name": "Salary Expense"},
                    {"code": "520002", "name": "Rent Expense"},
                    {"code": "520003", "name": "Utilities Expense"},
                    {"code": "520004", "name": "Internet Expense"},
                    {"code": "520005", "name": "Office Expense"},
                    {"code": "520006", "name": "Repair and Maintenance"},
                    {"code": "520007", "name": "Marketing Expense"},
                    {"code": "520008", "name": "Travel Expense"},
                    {"code": "520009", "name": "Bank Charges"},
                    {"code": "520010", "name": "Insurance Expense"},
                    {"code": "520011", "name": "Cleaning Expense"},
                    {"code": "520012", "name": "Training Expense"},
                    {"code": "520013", "name": "Miscellaneous Expense"},
                ],
            },
            {
                "code": "5300",
                "name": "Depreciation Expenses",
                "children": [
                    {"code": "530001", "name": "Depreciation Expense - Building", "is_depreciation": True},
                    {"code": "530002", "name": "Depreciation Expense - Furniture and Fixtures", "is_depreciation": True},
                    {"code": "530003", "name": "Depreciation Expense - Office Equipment", "is_depreciation": True},
                    {"code": "530004", "name": "Depreciation Expense - Computer Equipment", "is_depreciation": True},
                    {"code": "530005", "name": "Depreciation Expense - Gym Equipment", "is_depreciation": True},
                    {"code": "530006", "name": "Depreciation Expense - Vehicles", "is_depreciation": True},
                    {"code": "530007", "name": "Interest Expense"},
                ],
            },
        ],
    },
]


def _flatten_codes(nodes):
    codes = []
    for node in nodes:
        codes.append(node["code"])
        codes.extend(_flatten_codes(node.get("children", [])))
    return codes


def _seed_nodes(ChartOfAccount, nodes, parent=None, level=1):
    for index, item in enumerate(nodes, start=1):
        obj, _created = ChartOfAccount.objects.update_or_create(
            code=item["code"],
            defaults={
                "parent": parent,
                "name": item["name"],
                "account_type": item.get("account_type") or getattr(parent, "account_type", ""),
                "report_type": item.get("report_type") or getattr(parent, "report_type", ""),
                "report_level": level,
                "allow_direct_posting": item.get("allow_direct_posting", not item.get("children")),
                "is_depreciation": item.get("is_depreciation", False),
                "sort_order": index,
                "is_active": True,
                "remarks": "Seeded chart of account.",
            },
        )
        if item.get("children"):
            _seed_nodes(ChartOfAccount, item["children"], parent=obj, level=level + 1)


def seed_chart_of_accounts(apps, schema_editor):
    ChartOfAccount = apps.get_model("account", "ChartOfAccount")
    _seed_nodes(ChartOfAccount, SEED_CHART)


def unseed_chart_of_accounts(apps, schema_editor):
    ChartOfAccount = apps.get_model("account", "ChartOfAccount")
    ChartOfAccount.objects.filter(code__in=_flatten_codes(SEED_CHART)).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0018_locationtype_location"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ChartOfAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("code", models.CharField(blank=True, max_length=30, unique=True)),
                (
                    "account_type",
                    models.CharField(
                        choices=[
                            ("asset", "Asset"),
                            ("liability", "Liability"),
                            ("equity", "Equity"),
                            ("income", "Income"),
                            ("expense", "Expense"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "report_type",
                    models.CharField(
                        choices=[
                            ("balance_sheet", "Balance Sheet"),
                            ("profit_loss", "Profit & Loss"),
                        ],
                        editable=False,
                        max_length=20,
                    ),
                ),
                ("report_level", models.PositiveIntegerField(default=1, editable=False)),
                ("allow_direct_posting", models.BooleanField(default=True)),
                ("is_depreciation", models.BooleanField(default=False)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "branch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="account_chart_of_accounts",
                        to="core.branch",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="account_chart_of_accounts_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="account_chart_of_accounts",
                        to="core.fiscalyear",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="account_chart_of_accounts",
                        to="core.organization",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="account.chartofaccount",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="account_chart_of_accounts_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["code", "sort_order", "name"],
            },
        ),
        migrations.AddConstraint(
            model_name="chartofaccount",
            constraint=models.UniqueConstraint(
                fields=("parent", "name", "branch"),
                name="unique_chart_of_account_name_per_parent_branch",
            ),
        ),
        migrations.RunPython(seed_chart_of_accounts, unseed_chart_of_accounts),
    ]

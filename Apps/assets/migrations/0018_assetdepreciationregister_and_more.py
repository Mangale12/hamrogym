# Generated manually on 2026-04-16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0007_remove_journalline_credit_amount_and_more"),
        ("assets", "0017_assettransfer"),
        ("core", "0018_locationtype_location"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="depreciation_start_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="assetcategory",
            name="accumulated_depreciation_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="asset_category_accumulated_depreciation_accounts",
                to="account.chartofaccount",
            ),
        ),
        migrations.AddField(
            model_name="assetcategory",
            name="default_useful_life_months",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="assetcategory",
            name="depreciation_expense_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="asset_category_depreciation_expense_accounts",
                to="account.chartofaccount",
            ),
        ),
        migrations.AddField(
            model_name="assetcategory",
            name="depreciation_method",
            field=models.CharField(
                choices=[("straight_line", "Straight Line")],
                default="straight_line",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="assetcategory",
            name="fixed_asset_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="asset_category_fixed_asset_accounts",
                to="account.chartofaccount",
            ),
        ),
        migrations.CreateModel(
            name="AssetDepreciationRegister",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("schedule_month", models.DateField()),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("method", models.CharField(default="straight_line", max_length=30)),
                ("life_month_index", models.PositiveIntegerField(default=1)),
                ("useful_life_months", models.PositiveIntegerField(default=1)),
                ("purchase_cost", models.DecimalField(decimal_places=2, default="0.00", max_digits=14)),
                ("salvage_value", models.DecimalField(decimal_places=2, default="0.00", max_digits=14)),
                ("depreciable_amount", models.DecimalField(decimal_places=2, default="0.00", max_digits=14)),
                ("depreciation_amount", models.DecimalField(decimal_places=2, default="0.00", max_digits=14)),
                ("opening_book_value", models.DecimalField(decimal_places=2, default="0.00", max_digits=14)),
                ("closing_book_value", models.DecimalField(decimal_places=2, default="0.00", max_digits=14)),
                ("status", models.CharField(choices=[("unposted", "Unposted"), ("posted", "Posted")], default="unposted", max_length=20)),
                ("posted_at", models.DateTimeField(blank=True, null=True)),
                ("remarks", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "accumulated_depreciation_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="asset_depreciation_accumulated_entries",
                        to="account.chartofaccount",
                    ),
                ),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="depreciation_register_entries",
                        to="assets.asset",
                    ),
                ),
                (
                    "branch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="asset_depreciation_register_entries",
                        to="core.branch",
                    ),
                ),
                (
                    "depreciation_expense_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="asset_depreciation_expense_entries",
                        to="account.chartofaccount",
                    ),
                ),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="asset_depreciation_register_entries",
                        to="core.fiscalyear",
                    ),
                ),
                (
                    "fixed_asset_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="asset_depreciation_fixed_asset_entries",
                        to="account.chartofaccount",
                    ),
                ),
                (
                    "journal_entry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="asset_depreciation_entries",
                        to="account.journalentry",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="asset_depreciation_register_entries",
                        to="core.organization",
                    ),
                ),
                (
                    "posted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="asset_depreciation_posted_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-schedule_month", "asset__name", "-id"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("asset", "schedule_month", "branch"),
                        name="unique_asset_depreciation_register_asset_month_branch",
                    )
                ],
            },
        ),
    ]

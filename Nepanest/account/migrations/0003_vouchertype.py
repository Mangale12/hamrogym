# Generated manually on 2026-04-15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


VOUCHER_TYPES = [
    {"code": "PAY", "name": "Payment", "affects_cash": True},
    {"code": "REC", "name": "Receipt", "affects_cash": True},
    {"code": "JV", "name": "Journal", "affects_cash": False},
    {"code": "CON", "name": "Contra", "affects_cash": True},
    {"code": "PUR", "name": "Purchase", "affects_cash": False},
    {"code": "SAL", "name": "Sales", "affects_cash": False},
]


def seed_voucher_types(apps, schema_editor):
    VoucherType = apps.get_model("account", "VoucherType")
    for item in VOUCHER_TYPES:
        VoucherType.objects.update_or_create(
            code=item["code"],
            defaults={
                "name": item["name"],
                "affects_cash": item["affects_cash"],
                "is_active": True,
                "remarks": "Seeded voucher type.",
            },
        )


def unseed_voucher_types(apps, schema_editor):
    VoucherType = apps.get_model("account", "VoucherType")
    VoucherType.objects.filter(code__in=[item["code"] for item in VOUCHER_TYPES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_chartofaccount_is_ledger_ledger"),
        ("core", "0018_locationtype_location"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="VoucherType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("name", models.CharField(max_length=100)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("affects_cash", models.BooleanField(default=False)),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_branch_records", to="core.branch")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_created_records", to=settings.AUTH_USER_MODEL)),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_organization_records", to="core.organization")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_updated_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["name", "id"],
            },
        ),
        migrations.AddConstraint(
            model_name="vouchertype",
            constraint=models.UniqueConstraint(fields=("name", "branch"), name="unique_account_voucher_type_name_branch"),
        ),
        migrations.RunPython(seed_voucher_types, unseed_voucher_types),
    ]

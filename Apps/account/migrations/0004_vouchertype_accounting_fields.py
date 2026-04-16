# Generated manually on 2026-04-15

from django.db import migrations, models


VOUCHER_DEFAULTS = {
    "PAY": {
        "category": "cash",
        "nature": "credit_based",
        "affects_cash": True,
        "affects_bank": False,
        "auto_numbering": True,
        "prefix": "PAY-",
        "requires_reference": True,
        "requires_approval": False,
        "allow_negative": False,
        "is_system_generated": False,
        "description": "Payment voucher.",
    },
    "REC": {
        "category": "cash",
        "nature": "debit_based",
        "affects_cash": True,
        "affects_bank": False,
        "auto_numbering": True,
        "prefix": "REC-",
        "requires_reference": True,
        "requires_approval": False,
        "allow_negative": False,
        "is_system_generated": False,
        "description": "Receipt voucher.",
    },
    "JV": {
        "category": "journal",
        "nature": "both",
        "affects_cash": False,
        "affects_bank": False,
        "auto_numbering": True,
        "prefix": "JRN-",
        "requires_reference": False,
        "requires_approval": False,
        "allow_negative": False,
        "is_system_generated": False,
        "description": "Journal voucher.",
    },
    "CON": {
        "category": "bank",
        "nature": "both",
        "affects_cash": True,
        "affects_bank": True,
        "auto_numbering": True,
        "prefix": "CON-",
        "requires_reference": False,
        "requires_approval": False,
        "allow_negative": False,
        "is_system_generated": False,
        "description": "Contra voucher.",
    },
    "PUR": {
        "category": "purchase",
        "nature": "debit_based",
        "affects_cash": False,
        "affects_bank": False,
        "auto_numbering": True,
        "prefix": "PUR-",
        "requires_reference": True,
        "requires_approval": False,
        "allow_negative": False,
        "is_system_generated": False,
        "description": "Purchase voucher.",
    },
    "SAL": {
        "category": "sales",
        "nature": "credit_based",
        "affects_cash": False,
        "affects_bank": False,
        "auto_numbering": True,
        "prefix": "SAL-",
        "requires_reference": True,
        "requires_approval": False,
        "allow_negative": False,
        "is_system_generated": False,
        "description": "Sales voucher.",
    },
}


def populate_voucher_type_fields(apps, schema_editor):
    VoucherType = apps.get_model("account", "VoucherType")
    for voucher in VoucherType.objects.all():
        defaults = VOUCHER_DEFAULTS.get(voucher.code, {})
        voucher.category = defaults.get("category", "adjustment")
        voucher.nature = defaults.get("nature", "both")
        voucher.affects_cash = defaults.get("affects_cash", voucher.affects_cash)
        voucher.affects_bank = defaults.get("affects_bank", False)
        voucher.auto_numbering = defaults.get("auto_numbering", True)
        voucher.prefix = defaults.get("prefix", f"{voucher.code}-")
        voucher.last_number = voucher.last_number or 0
        voucher.requires_reference = defaults.get("requires_reference", False)
        voucher.requires_approval = defaults.get("requires_approval", False)
        voucher.allow_negative = defaults.get("allow_negative", False)
        voucher.is_system_generated = defaults.get("is_system_generated", False)
        voucher.description = (voucher.remarks or "").strip() or defaults.get("description", "")
        voucher.save(
            update_fields=[
                "category",
                "nature",
                "affects_cash",
                "affects_bank",
                "auto_numbering",
                "prefix",
                "last_number",
                "requires_reference",
                "requires_approval",
                "allow_negative",
                "is_system_generated",
                "description",
            ]
        )


def reverse_populate_voucher_type_fields(apps, schema_editor):
    VoucherType = apps.get_model("account", "VoucherType")
    for voucher in VoucherType.objects.all():
        voucher.remarks = (voucher.description or "").strip()
        voucher.save(update_fields=["remarks"])


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0003_vouchertype"),
    ]

    operations = [
        migrations.AddField(
            model_name="vouchertype",
            name="affects_bank",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="allow_negative",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="auto_numbering",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="category",
            field=models.CharField(choices=[("cash", "Cash"), ("bank", "Bank"), ("journal", "Journal"), ("sales", "Sales"), ("purchase", "Purchase"), ("adjustment", "Adjustment")], default="journal", max_length=20),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="is_system_generated",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="last_number",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="nature",
            field=models.CharField(choices=[("debit_based", "Debit Based"), ("credit_based", "Credit Based"), ("both", "Both")], default="both", max_length=20),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="prefix",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="requires_approval",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="vouchertype",
            name="requires_reference",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(populate_voucher_type_fields, reverse_populate_voucher_type_fields),
        migrations.RemoveField(
            model_name="vouchertype",
            name="remarks",
        ),
    ]

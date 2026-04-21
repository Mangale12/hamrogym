from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0003_discount_discountrule"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentMethod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=30, unique=True)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("category", models.CharField(choices=[("cash", "Cash"), ("bank", "Bank"), ("wallet", "Digital Wallet"), ("qr", "QR Payment"), ("card", "Card"), ("cheque", "Cheque")], default="bank", max_length=20)),
                ("provider", models.CharField(blank=True, max_length=120)),
                ("sequence", models.PositiveIntegerField(default=1)),
                ("is_digital", models.BooleanField(default=False)),
                ("supports_online", models.BooleanField(default=False)),
                ("supports_qr", models.BooleanField(default=False)),
                ("requires_reference", models.BooleanField(default=False)),
                ("is_default", models.BooleanField(default=False)),
            ],
            options={"ordering": ["sequence", "name", "id"]},
        ),
    ]

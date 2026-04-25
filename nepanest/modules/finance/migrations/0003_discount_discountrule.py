import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_party"),
        ("finance", "0002_taxrule_party_type_country"),
    ]

    operations = [
        migrations.CreateModel(
            name="Discount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=30, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("discount_type", models.CharField(choices=[("percentage", "Percentage"), ("fixed", "Fixed Amount")], default="percentage", max_length=20)),
                ("value", models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ("scope", models.CharField(choices=[("line", "Line"), ("document", "Document")], default="line", max_length=20)),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_branch_records", to="core.branch")),
                ("fiscal_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_fiscal_year_records", to="core.fiscalyear")),
            ],
            options={"ordering": ["name", "id"]},
        ),
        migrations.CreateModel(
            name="DiscountRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("min_quantity", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("min_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("priority", models.PositiveIntegerField(default=1)),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_branch_records", to="core.branch")),
                ("discount", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="finance.discount")),
                ("fiscal_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_fiscal_year_records", to="core.fiscalyear")),
                ("party_type", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.partytype")),
            ],
            options={"ordering": ["priority", "name", "id"]},
        ),
    ]

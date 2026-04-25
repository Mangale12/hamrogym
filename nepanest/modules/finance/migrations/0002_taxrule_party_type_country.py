import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0019_partytype"),
        ("finance", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="taxrule",
            name="country",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tax_rules",
                to="core.country",
            ),
        ),
        migrations.AddField(
            model_name="taxrule",
            name="party_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tax_rules",
                to="core.partytype",
            ),
        ),
    ]

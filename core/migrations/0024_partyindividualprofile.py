# Generated manually to add shared individual-party profile data.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_party"),
    ]

    operations = [
        migrations.CreateModel(
            name="PartyIndividualProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
                        max_length=20,
                    ),
                ),
                ("photo", models.ImageField(blank=True, null=True, upload_to="party/individual_photos/")),
                (
                    "party",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="individual_profile",
                        to="core.party",
                    ),
                ),
            ],
            options={
                "ordering": ["party_id"],
            },
        ),
    ]

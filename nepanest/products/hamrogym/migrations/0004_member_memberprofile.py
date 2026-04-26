# Generated manually for HamroGym member management.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_partyindividualprofile"),
        ("hamrogym", "0003_seed_common_gym_facilities"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Member",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("member_code", models.CharField(blank=True, max_length=30, unique=True)),
                ("join_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("inactive", "Inactive"), ("suspended", "Suspended")],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("emergency_contact_name", models.CharField(blank=True, max_length=255)),
                ("emergency_contact_phone", models.CharField(blank=True, max_length=30)),
                (
                    "branch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="%(app_label)s_%(class)s_branch_records",
                        to="core.branch",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_created_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="%(app_label)s_%(class)s_fiscal_year_records",
                        to="core.fiscalyear",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="%(app_label)s_%(class)s_organization_records",
                        to="core.organization",
                    ),
                ),
                (
                    "party",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="hamrogym_member",
                        to="core.party",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_updated_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["member_code", "id"],
            },
        ),
        migrations.CreateModel(
            name="MemberProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("height", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("weight", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                (
                    "fitness_goal",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("weight_loss", "Weight Loss"),
                            ("muscle_gain", "Muscle Gain"),
                            ("general_fitness", "General Fitness"),
                            ("strength", "Strength"),
                            ("rehabilitation", "Rehabilitation"),
                        ],
                        max_length=30,
                    ),
                ),
                ("medical_conditions", models.TextField(blank=True)),
                (
                    "member",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to="hamrogym.member",
                    ),
                ),
            ],
            options={
                "ordering": ["member_id"],
            },
        ),
    ]

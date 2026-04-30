# Generated manually for HamroGym member referrals.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_partyindividualprofile"),
        ("hamrogym", "0011_membertag"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MemberReferral",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("referral_date", models.DateField()),
                ("notes", models.TextField(blank=True)),
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
                    "referred_member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="referrals_received",
                        to="hamrogym.member",
                    ),
                ),
                (
                    "referrer_member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="referrals_made",
                        to="hamrogym.member",
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
                "ordering": ["-referral_date", "-id"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("referrer_member", "referred_member"),
                        name="unique_hamrogym_member_referral_pair",
                    ),
                ],
            },
        ),
    ]

# Generated manually for HamroGym membership entities.

from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("hamrogym", "0006_remove_memberprofile_fitness_goal_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("name", models.CharField(max_length=100)),
                ("code", models.CharField(max_length=50)),
                ("description", models.TextField(blank=True)),
                (
                    "branch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_accesstype_branch_records",
                        to="core.branch",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hamrogym_accesstype_created_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_accesstype_fiscal_year_records",
                        to="core.fiscalyear",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_accesstype_organization_records",
                        to="core.organization",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hamrogym_accesstype_updated_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "constraints": [
                    models.UniqueConstraint(fields=("name", "branch"), name="unique_hamrogym_access_type_name_branch"),
                    models.UniqueConstraint(fields=("code", "branch"), name="unique_hamrogym_access_type_code_branch"),
                ],
            },
        ),
        migrations.CreateModel(
            name="MembershipPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("name", models.CharField(max_length=150)),
                ("duration_days", models.PositiveIntegerField()),
                ("session_limit", models.PositiveIntegerField(blank=True, null=True)),
                ("freeze_limit_days", models.PositiveIntegerField(default=0)),
                ("description", models.TextField(blank=True)),
                (
                    "access_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="membership_plans",
                        to="hamrogym.accesstype",
                    ),
                ),
                (
                    "branch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_membershipplan_branch_records",
                        to="core.branch",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hamrogym_membershipplan_created_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_membershipplan_fiscal_year_records",
                        to="core.fiscalyear",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_membershipplan_organization_records",
                        to="core.organization",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hamrogym_membershipplan_updated_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "constraints": [
                    models.UniqueConstraint(fields=("name", "branch"), name="unique_hamrogym_membership_plan_name_branch")
                ],
            },
        ),
        migrations.CreateModel(
            name="MemberMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("allowed_sessions", models.PositiveIntegerField(blank=True, null=True)),
                ("used_sessions", models.PositiveIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("expired", "Expired"), ("paused", "Paused")],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("remarks", models.TextField(blank=True)),
                (
                    "branch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_membermembership_branch_records",
                        to="core.branch",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hamrogym_membermembership_created_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_membermembership_fiscal_year_records",
                        to="core.fiscalyear",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="memberships",
                        to="hamrogym.member",
                    ),
                ),
                (
                    "membership_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="member_memberships",
                        to="hamrogym.membershipplan",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_membermembership_organization_records",
                        to="core.organization",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hamrogym_membermembership_updated_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-start_date", "-id"]},
        ),
        migrations.CreateModel(
            name="MembershipFreeze",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("reason", models.TextField(blank=True)),
                ("remarks", models.TextField(blank=True)),
                (
                    "branch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_membershipfreeze_branch_records",
                        to="core.branch",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hamrogym_membershipfreeze_created_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_membershipfreeze_fiscal_year_records",
                        to="core.fiscalyear",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="membership_freezes",
                        to="hamrogym.member",
                    ),
                ),
                (
                    "membership",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="freezes",
                        to="hamrogym.membermembership",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="hamrogym_membershipfreeze_organization_records",
                        to="core.organization",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hamrogym_membershipfreeze_updated_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-start_date", "-id"]},
        ),
    ]

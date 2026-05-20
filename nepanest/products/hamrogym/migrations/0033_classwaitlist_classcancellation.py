import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_partyindividualprofile"),
        ("hamrogym", "0032_classbooking_classattendance"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ClassWaitlist",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("waitlist_position", models.PositiveIntegerField()),
                ("promoted_at", models.DateTimeField(blank=True, null=True)),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_branch_records", to="core.branch")),
                ("class_session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="waitlists", to="hamrogym.classsession")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_created_records", to=settings.AUTH_USER_MODEL)),
                ("fiscal_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_fiscal_year_records", to="core.fiscalyear")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="class_waitlists", to="hamrogym.member")),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_organization_records", to="core.organization")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_updated_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["waitlist_position", "id"],
                "constraints": [
                    models.UniqueConstraint(fields=("class_session", "member"), name="unique_hamrogym_class_waitlist_member_session"),
                    models.UniqueConstraint(fields=("class_session", "waitlist_position"), name="unique_hamrogym_class_waitlist_position_session"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ClassCancellation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("cancelled_by", models.CharField(choices=[("member", "Member"), ("trainer", "Trainer"), ("admin", "Admin")], default="admin", max_length=20)),
                ("reason", models.TextField(blank=True)),
                ("cancellation_time", models.DateTimeField(default=django.utils.timezone.now)),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_branch_records", to="core.branch")),
                ("class_session", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="cancellation", to="hamrogym.classsession")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_created_records", to=settings.AUTH_USER_MODEL)),
                ("fiscal_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_fiscal_year_records", to="core.fiscalyear")),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_organization_records", to="core.organization")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_updated_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-cancellation_time", "-id"],
            },
        ),
    ]

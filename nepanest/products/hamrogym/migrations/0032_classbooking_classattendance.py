import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_partyindividualprofile"),
        ("hamrogym", "0031_classsession"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ClassBooking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("booked", "Booked"), ("cancelled", "Cancelled")], default="booked", max_length=20)),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_branch_records", to="core.branch")),
                ("class_session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookings", to="hamrogym.classsession")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_created_records", to=settings.AUTH_USER_MODEL)),
                ("fiscal_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_fiscal_year_records", to="core.fiscalyear")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="class_bookings", to="hamrogym.member")),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_organization_records", to="core.organization")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_updated_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["class_session__session_date", "member__member_code", "id"],
                "constraints": [
                    models.UniqueConstraint(fields=("class_session", "member"), name="unique_hamrogym_class_booking_member_session"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ClassAttendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("present", "Present"), ("absent", "Absent"), ("late", "Late")], default="present", max_length=20)),
                ("checked_in_at", models.DateTimeField(blank=True, null=True)),
                ("booking", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="attendance_records", to="hamrogym.classbooking")),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_branch_records", to="core.branch")),
                ("class_session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="hamrogym.classsession")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_created_records", to=settings.AUTH_USER_MODEL)),
                ("fiscal_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_fiscal_year_records", to="core.fiscalyear")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="class_attendance_records", to="hamrogym.member")),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_organization_records", to="core.organization")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_updated_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["class_session__session_date", "member__member_code", "id"],
                "constraints": [
                    models.UniqueConstraint(fields=("class_session", "member"), name="unique_hamrogym_class_attendance_member_session"),
                ],
            },
        ),
    ]

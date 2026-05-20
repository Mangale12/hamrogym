import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_partyindividualprofile"),
        ("hamrogym", "0029_alter_gymclasstype_table"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ClassSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                (
                    "day_of_week",
                    models.CharField(
                        choices=[
                            ("monday", "Monday"),
                            ("tuesday", "Tuesday"),
                            ("wednesday", "Wednesday"),
                            ("thursday", "Thursday"),
                            ("friday", "Friday"),
                            ("saturday", "Saturday"),
                            ("sunday", "Sunday"),
                        ],
                        max_length=10,
                    ),
                ),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_branch_records", to="core.branch")),
                ("class_room", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="class_schedules", to="hamrogym.classroom")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_created_records", to=settings.AUTH_USER_MODEL)),
                ("fiscal_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_fiscal_year_records", to="core.fiscalyear")),
                ("gym_class", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="class_schedules", to="hamrogym.gymclass")),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_organization_records", to="core.organization")),
                ("trainer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="class_schedules", to="hamrogym.trainer")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_updated_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["day_of_week", "start_time", "gym_class__name", "id"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("gym_class", "day_of_week", "start_time", "end_time", "class_room"),
                        name="unique_hamrogym_class_schedule_slot",
                    ),
                ],
            },
        ),
    ]

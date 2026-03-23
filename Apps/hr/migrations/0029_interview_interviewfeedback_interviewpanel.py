from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0016_fiscalyear_is_current"),
        ("hr", "0028_interviewstage"),
    ]

    operations = [
        migrations.CreateModel(
            name="Interview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "scheduled_at",
                    models.DateTimeField(),
                ),
                ("location", models.CharField(max_length=255)),
                (
                    "mode",
                    models.CharField(
                        choices=[
                            ("in_person", "In Person"),
                            ("video", "Video"),
                            ("phone", "Phone"),
                        ],
                        default="in_person",
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("scheduled", "Scheduled"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="scheduled",
                        max_length=50,
                    ),
                ),
                (
                    "sequence",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Auto-assigned stage order for this application's interview flow.",
                        null=True,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        help_text="Fiscal year",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.fiscalyear",
                    ),
                ),
                (
                    "interview_stage",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interviews",
                        to="hr.interviewstage",
                    ),
                ),
                (
                    "job_application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interviews",
                        to="hr.jobapplication",
                    ),
                ),
            ],
            options={
                "ordering": ["job_application", "sequence", "scheduled_at", "id"],
            },
        ),
        migrations.CreateModel(
            name="InterviewFeedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.PositiveIntegerField()),
                ("comments", models.TextField(blank=True)),
                (
                    "recommendation",
                    models.CharField(
                        choices=[
                            ("hire", "Hire"),
                            ("reject", "Reject"),
                            ("next_round", "Next Round"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "interview",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedbacks",
                        to="hr.interview",
                    ),
                ),
                (
                    "panel_member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interview_feedbacks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InterviewPanel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        help_text="Fiscal year",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.fiscalyear",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interview_panel",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "interview",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="panel_members",
                        to="hr.interview",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="interview",
            constraint=models.UniqueConstraint(
                fields=("job_application", "interview_stage"),
                name="unique_interview_stage_per_application",
            ),
        ),
        migrations.AddConstraint(
            model_name="interview",
            constraint=models.UniqueConstraint(
                fields=("job_application", "sequence"),
                name="unique_interview_sequence_per_application",
            ),
        ),
        migrations.AddConstraint(
            model_name="interviewfeedback",
            constraint=models.UniqueConstraint(
                fields=("interview", "panel_member"),
                name="unique_feedback_per_panel_member",
            ),
        ),
        migrations.AddConstraint(
            model_name="interviewpanel",
            constraint=models.UniqueConstraint(
                fields=("interview", "employee"),
                name="unique_employee_per_interview_panel",
            ),
        ),
    ]

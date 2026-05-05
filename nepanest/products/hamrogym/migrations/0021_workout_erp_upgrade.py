# Generated manually for ERP-oriented workout structure upgrades on 2026-05-05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def populate_workout_day_plan_and_title(apps, schema_editor):
    WorkoutDay = apps.get_model("hamrogym", "WorkoutDay")

    for day in WorkoutDay.objects.select_related("workout_week", "workout_week__workout_plan").all():
        updates = []
        if day.workout_week_id and day.workout_plan_id is None:
            day.workout_plan_id = day.workout_week.workout_plan_id
            updates.append("workout_plan")
        if not day.title:
            day.title = f"Day {day.day_number}"
            updates.append("title")
        if updates:
            day.save(update_fields=updates)


class Migration(migrations.Migration):

    dependencies = [
        ("hamrogym", "0020_workout_planning_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="workoutday",
            name="title",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workoutday",
            name="workout_plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="days",
                to="hamrogym.workoutplan",
            ),
        ),
        migrations.AlterField(
            model_name="workoutday",
            name="workout_week",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="days",
                to="hamrogym.workoutweek",
            ),
        ),
        migrations.RunPython(populate_workout_day_plan_and_title, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name="workoutday",
            options={"ordering": ["day_number", "id"]},
        ),
        migrations.AlterField(
            model_name="workoutday",
            name="workout_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="days",
                to="hamrogym.workoutplan",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="workoutday",
            name="unique_hamrogym_workout_day_number_per_week",
        ),
        migrations.AddConstraint(
            model_name="workoutday",
            constraint=models.UniqueConstraint(
                fields=("workout_plan", "day_number"),
                name="unique_hamrogym_workout_day_number_per_plan",
            ),
        ),
        migrations.AlterField(
            model_name="workoutexercise",
            name="duration_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="workoutexercise",
            name="exercise",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="planned_workouts",
                to="hamrogym.exercise",
            ),
        ),
        migrations.AlterField(
            model_name="workoutexercise",
            name="reps",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="workoutexercise",
            name="rest_time_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="workoutexercise",
            name="sets",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="workoutexercise",
            name="workout_day",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exercises",
                to="hamrogym.workoutday",
            ),
        ),
        migrations.AlterField(
            model_name="workoutassignment",
            name="member",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="workout_assignments",
                to="hamrogym.member",
            ),
        ),
        migrations.AlterField(
            model_name="workoutassignment",
            name="trainer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="workout_assignments",
                to="hamrogym.trainer",
            ),
        ),
        migrations.AlterField(
            model_name="workoutassignment",
            name="workout_plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="assignments",
                to="hamrogym.workoutplan",
            ),
        ),
        migrations.AlterModelOptions(
            name="workoutlog",
            options={"ordering": ["-date", "-id"]},
        ),
        migrations.AlterField(
            model_name="workoutlog",
            name="exercise",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="workout_logs",
                to="hamrogym.exercise",
            ),
        ),
        migrations.AlterField(
            model_name="workoutlog",
            name="member",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="workout_logs",
                to="hamrogym.member",
            ),
        ),
        migrations.AlterField(
            model_name="workoutlog",
            name="workout_assignment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="logs",
                to="hamrogym.workoutassignment",
            ),
        ),
        migrations.AlterField(
            model_name="workoutlog",
            name="workout_day",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="logs",
                to="hamrogym.workoutday",
            ),
        ),
        migrations.CreateModel(
            name="PersonalBest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("best_weight", models.FloatField(blank=True, null=True)),
                ("best_reps", models.IntegerField(blank=True, null=True)),
                ("best_duration", models.IntegerField(blank=True, null=True)),
                ("achieved_on", models.DateField()),
                ("branch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_branch_records", to="core.branch")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_created_records", to=settings.AUTH_USER_MODEL)),
                ("exercise", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="personal_bests", to="hamrogym.exercise")),
                ("fiscal_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_fiscal_year_records", to="core.fiscalyear")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="personal_bests", to="hamrogym.member")),
                ("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name="%(app_label)s_%(class)s_organization_records", to="core.organization")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_updated_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["member_id", "exercise_id"]},
        ),
        migrations.CreateModel(
            name="WorkoutPlanVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version_number", models.IntegerField()),
                ("change_notes", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("workout_plan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="versions", to="hamrogym.workoutplan")),
            ],
            options={"ordering": ["-version_number", "-id"]},
        ),
        migrations.AddConstraint(
            model_name="personalbest",
            constraint=models.UniqueConstraint(
                fields=("member", "exercise"),
                name="unique_hamrogym_personal_best_member_exercise",
            ),
        ),
        migrations.AddConstraint(
            model_name="workoutplanversion",
            constraint=models.UniqueConstraint(
                fields=("workout_plan", "version_number"),
                name="unique_hamrogym_plan_version_number",
            ),
        ),
    ]

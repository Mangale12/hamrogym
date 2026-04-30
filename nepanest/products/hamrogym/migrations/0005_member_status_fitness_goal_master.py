# Generated manually for HamroGym member status and fitness goal master data.

import django.db.models.deletion
from django.db import migrations, models


COMMON_MEMBER_STATUSES = (
    ("active", "Active", "Currently active members with valid membership access."),
    ("inactive", "Inactive", "Members who are not currently using the membership."),
    ("suspended", "Suspended", "Members whose access is temporarily restricted."),
)

COMMON_FITNESS_GOALS = (
    ("weight_loss", "Weight Loss", "Focused on reducing body weight and fat percentage."),
    ("muscle_gain", "Muscle Gain", "Focused on building lean muscle mass."),
    ("general_fitness", "General Fitness", "Focused on overall health, stamina, and mobility."),
    ("strength", "Strength", "Focused on improving physical strength and lifting capacity."),
    ("rehabilitation", "Rehabilitation", "Focused on recovery, corrective exercise, and safe conditioning."),
)


def seed_lookup_records(apps, schema_editor):
    Member = apps.get_model("hamrogym", "Member")
    MemberProfile = apps.get_model("hamrogym", "MemberProfile")
    MemberStatus = apps.get_model("hamrogym", "MemberStatus")
    FitnessGoal = apps.get_model("hamrogym", "FitnessGoal")

    status_by_code = {}
    for code, name, remarks in COMMON_MEMBER_STATUSES:
        status, _created = MemberStatus.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "remarks": remarks,
                "is_system": True,
                "is_active": True,
            },
        )
        status_by_code[code] = status

    goal_by_code = {}
    for code, name, remarks in COMMON_FITNESS_GOALS:
        goal, _created = FitnessGoal.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "remarks": remarks,
                "is_system": True,
                "is_active": True,
            },
        )
        goal_by_code[code] = goal

    default_status = status_by_code.get("active")

    for member in Member.objects.all():
        legacy_status = (getattr(member, "status", "") or "active").strip().lower()
        member.member_status = status_by_code.get(legacy_status, default_status)
        member.is_active = bool(member.member_status and member.member_status.code == "active")
        member.save(update_fields=["member_status", "is_active"])

    for profile in MemberProfile.objects.all():
        legacy_goal = (getattr(profile, "fitness_goal", "") or "").strip().lower()
        profile.fitness_goal_lookup = goal_by_code.get(legacy_goal)
        profile.save(update_fields=["fitness_goal_lookup"])


def unseed_lookup_records(apps, schema_editor):
    Member = apps.get_model("hamrogym", "Member")
    MemberProfile = apps.get_model("hamrogym", "MemberProfile")

    for member in Member.objects.select_related("member_status"):
        member.status = member.member_status.code if member.member_status_id else "active"
        member.save(update_fields=["status"])

    for profile in MemberProfile.objects.select_related("fitness_goal_lookup"):
        profile.fitness_goal = profile.fitness_goal_lookup.code if profile.fitness_goal_lookup_id else ""
        profile.save(update_fields=["fitness_goal"])


class Migration(migrations.Migration):

    dependencies = [
        ("hamrogym", "0004_member_memberprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="FitnessGoal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.CharField(max_length=50, unique=True)),
                ("is_system", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="MemberStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.CharField(max_length=50, unique=True)),
                ("is_system", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="memberprofile",
            name="fitness_goal_lookup",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="member_profiles",
                to="hamrogym.fitnessgoal",
            ),
        ),
        migrations.AddField(
            model_name="member",
            name="member_status",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="members",
                to="hamrogym.memberstatus",
            ),
        ),
        migrations.RunPython(seed_lookup_records, unseed_lookup_records),
        migrations.RemoveField(
            model_name="memberprofile",
            name="fitness_goal",
        ),
        migrations.RemoveField(
            model_name="member",
            name="status",
        ),
        migrations.RenameField(
            model_name="memberprofile",
            old_name="fitness_goal_lookup",
            new_name="fitness_goal",
        ),
        migrations.RenameField(
            model_name="member",
            old_name="member_status",
            new_name="status",
        ),
    ]

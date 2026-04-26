from django.db import migrations


COMMON_GYM_FACILITIES = (
    ("Cardio Zone", "Dedicated area for treadmills, cycles, and cardio workouts."),
    ("Weight Zone", "Strength training area with free weights and machines."),
    ("Functional Training Area", "Open workout space for mobility, HIIT, and circuit sessions."),
    ("Group Exercise Studio", "Shared studio for yoga, zumba, aerobics, and classes."),
    ("Locker Room", "Common changing and storage area for members."),
    ("Shower Area", "Common shower facility for post-workout use."),
    ("Reception", "Front desk and member assistance area."),
    ("Sauna", "Recovery and relaxation space for members after workouts."),
)


def seed_common_facilities(apps, schema_editor):
    Branch = apps.get_model("core", "Branch")
    GymFacility = apps.get_model("hamrogym", "GymFacility")

    for branch in Branch.objects.all():
        for facility_name, remarks in COMMON_GYM_FACILITIES:
            GymFacility.objects.update_or_create(
                branch=branch,
                name=facility_name,
                defaults={
                    "organization_id": branch.organization_id,
                    "remarks": remarks,
                    "is_active": True,
                },
            )


def unseed_common_facilities(apps, schema_editor):
    GymFacility = apps.get_model("hamrogym", "GymFacility")
    facility_names = [name for name, _remarks in COMMON_GYM_FACILITIES]
    GymFacility.objects.filter(name__in=facility_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("hamrogym", "0002_rename_description_gymfacility_remarks_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_common_facilities, unseed_common_facilities),
    ]

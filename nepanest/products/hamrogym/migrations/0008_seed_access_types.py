from django.db import migrations


COMMON_ACCESS_TYPES = (
    (
        "full_gym",
        "Full Gym",
        "Access to the full gym floor and standard workout areas.",
        "Default access type for general gym memberships.",
    ),
    (
        "classes_only",
        "Classes Only",
        "Access limited to instructor-led classes and group sessions.",
        "Use for memberships centered around class participation.",
    ),
    (
        "personal_training",
        "Personal Training",
        "Access intended for personal training sessions and related programs.",
        "Use for one-to-one or trainer-managed access packages.",
    ),
)


def seed_access_types(apps, schema_editor):
    Branch = apps.get_model("core", "Branch")
    AccessType = apps.get_model("hamrogym", "AccessType")

    for branch in Branch.objects.all():
        for code, name, description, remarks in COMMON_ACCESS_TYPES:
            AccessType.objects.update_or_create(
                branch=branch,
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "remarks": remarks,
                    "organization_id": branch.organization_id,
                    "is_active": True,
                },
            )


def unseed_access_types(apps, schema_editor):
    AccessType = apps.get_model("hamrogym", "AccessType")
    codes = [code for code, _name, _description, _remarks in COMMON_ACCESS_TYPES]
    AccessType.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("hamrogym", "0007_membership_entities"),
    ]

    operations = [
        migrations.RunPython(seed_access_types, unseed_access_types),
    ]

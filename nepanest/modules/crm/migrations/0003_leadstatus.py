from django.core.validators import RegexValidator
from django.db import migrations, models


HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r"^#(?:[0-9A-Fa-f]{6})$",
    message="Enter a valid hex color code like #3498DB.",
)


LEAD_STATUSES = [
    {
        "name": "New",
        "code": "new",
        "sequence": 0,
        "is_default": True,
        "is_active": True,
        "color": "#3498DB",
        "is_closed": False,
        "remarks": "Fresh lead waiting for first contact.",
    },
    {
        "name": "Contacted",
        "code": "contacted",
        "sequence": 1,
        "is_default": False,
        "is_active": True,
        "color": "#F39C12",
        "is_closed": False,
        "remarks": "Lead has been contacted by the team.",
    },
    {
        "name": "Interested",
        "code": "interested",
        "sequence": 2,
        "is_default": False,
        "is_active": True,
        "color": "#9B59B6",
        "is_closed": False,
        "remarks": "Lead has shown buying interest.",
    },
    {
        "name": "Follow Up",
        "code": "follow_up",
        "sequence": 3,
        "is_default": False,
        "is_active": True,
        "color": "#1ABC9C",
        "is_closed": False,
        "remarks": "Lead requires a follow-up activity.",
    },
    {
        "name": "Trial Booked",
        "code": "trial_booked",
        "sequence": 4,
        "is_default": False,
        "is_active": True,
        "color": "#16A085",
        "is_closed": False,
        "remarks": "A trial session has been booked.",
    },
    {
        "name": "Qualified",
        "code": "qualified",
        "sequence": 5,
        "is_default": False,
        "is_active": True,
        "color": "#2ECC71",
        "is_closed": False,
        "remarks": "Lead is qualified for conversion.",
    },
    {
        "name": "Converted",
        "code": "converted",
        "sequence": 6,
        "is_default": False,
        "is_active": True,
        "color": "#34495E",
        "is_closed": True,
        "remarks": "Lead has been converted into a customer.",
    },
    {
        "name": "Lost",
        "code": "lost",
        "sequence": 7,
        "is_default": False,
        "is_active": True,
        "color": "#E74C3C",
        "is_closed": True,
        "remarks": "Lead has been lost.",
    },
    {
        "name": "No Show",
        "code": "no_show",
        "sequence": 8,
        "is_default": False,
        "is_active": True,
        "color": "#E67E22",
        "is_closed": True,
        "remarks": "Lead did not show up for the booked trial.",
    },
    {
        "name": "Junk",
        "code": "junk",
        "sequence": 9,
        "is_default": False,
        "is_active": True,
        "color": "#7F8C8D",
        "is_closed": True,
        "remarks": "Lead is invalid or not worth pursuing.",
    },
]

def seed_lead_statuses(apps, schema_editor):
    LeadStatus = apps.get_model("crm", "LeadStatus")

    for status in LEAD_STATUSES:
        LeadStatus.objects.update_or_create(
            code=status["code"],
            defaults=status,
        )


def unseed_lead_statuses(apps, schema_editor):
    LeadStatus = apps.get_model("crm", "LeadStatus")
    LeadStatus.objects.filter(code__in=[status["code"] for status in LEAD_STATUSES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0002_seed_lead_sources"),
    ]

    operations = [
        migrations.CreateModel(
            name="LeadStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("remarks", models.TextField(blank=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("sequence", models.PositiveIntegerField(default=0)),
                ("is_default", models.BooleanField(default=False)),
                (
                    "color",
                    models.CharField(
                        default="#3498DB",
                        max_length=7,
                        validators=[HEX_COLOR_VALIDATOR],
                    ),
                ),
                ("is_closed", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["sequence", "name", "id"],
            },
        ),
        migrations.RunPython(seed_lead_statuses, unseed_lead_statuses),
    ]

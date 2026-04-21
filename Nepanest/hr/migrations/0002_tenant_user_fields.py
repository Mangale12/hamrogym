from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("hr", "0001_initial"),
        ("core", "0006_organization_branch"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="department",
            name="organization",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="core.organization"),
        ),
        migrations.AddField(
            model_name="department",
            name="branch",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="core.branch"),
        ),
        migrations.AddField(
            model_name="designation",
            name="organization",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="core.organization"),
        ),
        migrations.AddField(
            model_name="designation",
            name="branch",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="core.branch"),
        ),
        migrations.AddField(
            model_name="employee",
            name="organization",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="core.organization"),
        ),
        migrations.AddField(
            model_name="employee",
            name="branch",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="core.branch"),
        ),
        migrations.AddField(
            model_name="employee",
            name="user",
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="employee_profile", to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(model_name="employee", name="first_name"),
        migrations.RemoveField(model_name="employee", name="last_name"),
        migrations.RemoveField(model_name="employee", name="email"),
        migrations.RemoveField(model_name="employee", name="phone"),
    ]

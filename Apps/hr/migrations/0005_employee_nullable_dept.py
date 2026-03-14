from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("hr", "0004_employee_related_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="department",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="hr.department"),
        ),
        migrations.AlterField(
            model_name="employee",
            name="designation",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="hr.designation"),
        ),
    ]

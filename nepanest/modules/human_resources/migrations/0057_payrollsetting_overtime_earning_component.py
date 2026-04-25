from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("hr", "0056_payrollrun_fiscal_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="payrollsetting",
            name="overtime_earning_component",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payroll_settings_overtime_component",
                to="hr.salarycomponent",
            ),
        ),
    ]

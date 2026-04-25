from django.db import migrations, models
import django.db.models.deletion


def populate_payroll_run_fiscal_year(apps, schema_editor):
    PayrollRun = apps.get_model("hr", "PayrollRun")
    FiscalYear = apps.get_model("core", "FiscalYear")

    fallback_fiscal_year = (
        FiscalYear.objects.filter(is_current=True).order_by("-start_date", "-id").first()
        or FiscalYear.objects.filter(is_active=True).order_by("-start_date", "-id").first()
        or FiscalYear.objects.order_by("-start_date", "-id").first()
    )

    for payroll_run in PayrollRun.objects.all():
        fiscal_year = (
            FiscalYear.objects.filter(
                start_date__lte=payroll_run.period_end,
                end_date__gte=payroll_run.period_start,
            )
            .order_by("-start_date", "-id")
            .first()
        ) or fallback_fiscal_year

        if fiscal_year is None:
            raise RuntimeError("Cannot migrate payroll runs without at least one fiscal year record.")

        payroll_run.fiscal_year_id = fiscal_year.pk
        payroll_run.save(update_fields=["fiscal_year"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("hr", "0055_alter_payrollrun_payroll_month"),
    ]

    operations = [
        migrations.AddField(
            model_name="payrollrun",
            name="fiscal_year",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payroll_runs",
                to="core.fiscalyear",
            ),
        ),
        migrations.RunPython(populate_payroll_run_fiscal_year, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="payrollrun",
            name="fiscal_year",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="payroll_runs",
                to="core.fiscalyear",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="payrollrun",
            name="unique_payroll_run_scope_period",
        ),
        migrations.AddConstraint(
            model_name="payrollrun",
            constraint=models.UniqueConstraint(
                fields=("organization", "branch", "fiscal_year", "payroll_month"),
                name="unique_payroll_run_scope_fiscal_year_month",
            ),
        ),
    ]

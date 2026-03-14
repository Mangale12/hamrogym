from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("hr", "0002_tenant_user_fields"),
        ("core", "0006_organization_branch"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="employee_code",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="employee",
            name="middle_name",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="gender",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name="employee",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="nationality",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="hr_employees_nationality",
                to="core.country",
            ),
        ),
        migrations.AddField(
            model_name="employee",
            name="marital_status",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="employee",
            name="blood_group",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name="employee",
            name="profile_photo",
            field=models.ImageField(blank=True, null=True, upload_to="employee_photos/"),
        ),
        migrations.AddField(
            model_name="employee",
            name="phone",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="employee",
            name="alternate_phone",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="employee",
            name="address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="permanent_address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="city",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="employee",
            name="state",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="hr_employees_state",
                to="core.state",
            ),
        ),
        migrations.AddField(
            model_name="employee",
            name="country",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="hr_employees_country",
                to="core.country",
            ),
        ),
        migrations.AddField(
            model_name="employee",
            name="zip_code",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="employee",
            name="employee_type",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="employee",
            name="employment_status",
            field=models.CharField(blank=True, default="active", max_length=20),
        ),
        migrations.AddField(
            model_name="employee",
            name="reporting_manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reportees",
                to="hr.employee",
            ),
        ),
        migrations.AddField(
            model_name="employee",
            name="shift",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="probation_period",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="salary_type",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="employee",
            name="basic_salary",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="allowance",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="overtime_rate",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="tax_number",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="bank_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="employee",
            name="bank_account_number",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="bank_branch",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="employee",
            name="payment_method",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="employee",
            name="citizenship_no",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="passport_no",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="pan_no",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="social_security_no",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="insurance_no",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="job_description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="work_location",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="employee",
            name="work_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="employee",
            name="joining_letter",
            field=models.FileField(blank=True, null=True, upload_to="employee_documents/"),
        ),
        migrations.AddField(
            model_name="employee",
            name="contract_file",
            field=models.FileField(blank=True, null=True, upload_to="employee_documents/"),
        ),
        migrations.AddField(
            model_name="employee",
            name="attendance_required",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="leave_group",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="employee",
            name="weekly_off",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="emergency_contact_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="employee",
            name="relationship",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="emergency_phone",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="employee",
            name="emergency_address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="role",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="employee",
            name="permission_group",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="employee",
            name="login_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="resignation_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="last_working_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="exit_reason",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="employee",
            name="exit_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="employee",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="hr_employees_updated",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="EmployeeDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("doc_type", models.CharField(blank=True, max_length=100)),
                ("doc_number", models.CharField(blank=True, max_length=100)),
                ("file", models.FileField(blank=True, null=True, upload_to="employee_documents/")),
                ("issue_date", models.DateField(blank=True, null=True)),
                ("expiry_date", models.DateField(blank=True, null=True)),
                ("remarks", models.CharField(blank=True, max_length=255)),
                (
                    "employee",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["doc_type", "doc_number"],
            },
        ),
    ]

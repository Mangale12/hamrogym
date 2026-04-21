from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("hr", "0003_employee_extended"),
        ("core", "0006_organization_branch"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("middle_name", models.CharField(blank=True, max_length=50)),
                ("gender", models.CharField(blank=True, max_length=10)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("marital_status", models.CharField(blank=True, max_length=20)),
                ("blood_group", models.CharField(blank=True, max_length=10)),
                ("profile_photo", models.ImageField(blank=True, null=True, upload_to="employee_photos/")),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to="hr.employee"),
                ),
                (
                    "nationality",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="hr_employee_profiles_nationality",
                        to="core.country",
                    ),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeeContact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("alternate_phone", models.CharField(blank=True, max_length=30)),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="contact", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeeAddress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("address", models.TextField(blank=True)),
                ("permanent_address", models.TextField(blank=True)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("zip_code", models.CharField(blank=True, max_length=20)),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="address", to="hr.employee"),
                ),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="hr_employee_addresses_country",
                        to="core.country",
                    ),
                ),
                (
                    "state",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="hr_employee_addresses_state",
                        to="core.state",
                    ),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeePayroll",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("salary_type", models.CharField(blank=True, max_length=20)),
                ("basic_salary", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("allowance", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("overtime_rate", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("tax_number", models.CharField(blank=True, max_length=50)),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="payroll", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeeBank",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("bank_name", models.CharField(blank=True, max_length=100)),
                ("bank_account_number", models.CharField(blank=True, max_length=50)),
                ("bank_branch", models.CharField(blank=True, max_length=100)),
                ("payment_method", models.CharField(blank=True, max_length=20)),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="bank", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeeLegal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("citizenship_no", models.CharField(blank=True, max_length=50)),
                ("passport_no", models.CharField(blank=True, max_length=50)),
                ("pan_no", models.CharField(blank=True, max_length=50)),
                ("social_security_no", models.CharField(blank=True, max_length=50)),
                ("insurance_no", models.CharField(blank=True, max_length=50)),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="legal", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeeWork",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("job_description", models.TextField(blank=True)),
                ("work_location", models.CharField(blank=True, max_length=20)),
                ("work_email", models.EmailField(blank=True, max_length=254)),
                ("joining_letter", models.FileField(blank=True, null=True, upload_to="employee_documents/")),
                ("contract_file", models.FileField(blank=True, null=True, upload_to="employee_documents/")),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="work", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeeAttendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attendance_required", models.BooleanField(default=True)),
                ("leave_group", models.CharField(blank=True, max_length=100)),
                ("weekly_off", models.CharField(blank=True, max_length=50)),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="attendance", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeeEmergency",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("emergency_contact_name", models.CharField(blank=True, max_length=100)),
                ("relationship", models.CharField(blank=True, max_length=50)),
                ("emergency_phone", models.CharField(blank=True, max_length=30)),
                ("emergency_address", models.TextField(blank=True)),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="emergency", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeeAccess",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(blank=True, max_length=100)),
                ("permission_group", models.CharField(blank=True, max_length=100)),
                ("login_enabled", models.BooleanField(default=True)),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="access", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.CreateModel(
            name="EmployeeExit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("resignation_date", models.DateField(blank=True, null=True)),
                ("last_working_date", models.DateField(blank=True, null=True)),
                ("exit_reason", models.CharField(blank=True, max_length=255)),
                ("exit_notes", models.TextField(blank=True)),
                (
                    "employee",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="exit", to="hr.employee"),
                ),
            ],
            options={
                "ordering": ["employee__employee_id"],
            },
        ),
        migrations.RemoveField(model_name="employee", name="middle_name"),
        migrations.RemoveField(model_name="employee", name="gender"),
        migrations.RemoveField(model_name="employee", name="date_of_birth"),
        migrations.RemoveField(model_name="employee", name="nationality"),
        migrations.RemoveField(model_name="employee", name="marital_status"),
        migrations.RemoveField(model_name="employee", name="blood_group"),
        migrations.RemoveField(model_name="employee", name="profile_photo"),
        migrations.RemoveField(model_name="employee", name="phone"),
        migrations.RemoveField(model_name="employee", name="alternate_phone"),
        migrations.RemoveField(model_name="employee", name="address"),
        migrations.RemoveField(model_name="employee", name="permanent_address"),
        migrations.RemoveField(model_name="employee", name="city"),
        migrations.RemoveField(model_name="employee", name="state"),
        migrations.RemoveField(model_name="employee", name="country"),
        migrations.RemoveField(model_name="employee", name="zip_code"),
        migrations.RemoveField(model_name="employee", name="salary_type"),
        migrations.RemoveField(model_name="employee", name="basic_salary"),
        migrations.RemoveField(model_name="employee", name="allowance"),
        migrations.RemoveField(model_name="employee", name="overtime_rate"),
        migrations.RemoveField(model_name="employee", name="tax_number"),
        migrations.RemoveField(model_name="employee", name="bank_name"),
        migrations.RemoveField(model_name="employee", name="bank_account_number"),
        migrations.RemoveField(model_name="employee", name="bank_branch"),
        migrations.RemoveField(model_name="employee", name="payment_method"),
        migrations.RemoveField(model_name="employee", name="citizenship_no"),
        migrations.RemoveField(model_name="employee", name="passport_no"),
        migrations.RemoveField(model_name="employee", name="pan_no"),
        migrations.RemoveField(model_name="employee", name="social_security_no"),
        migrations.RemoveField(model_name="employee", name="insurance_no"),
        migrations.RemoveField(model_name="employee", name="job_description"),
        migrations.RemoveField(model_name="employee", name="work_location"),
        migrations.RemoveField(model_name="employee", name="work_email"),
        migrations.RemoveField(model_name="employee", name="joining_letter"),
        migrations.RemoveField(model_name="employee", name="contract_file"),
        migrations.RemoveField(model_name="employee", name="attendance_required"),
        migrations.RemoveField(model_name="employee", name="leave_group"),
        migrations.RemoveField(model_name="employee", name="weekly_off"),
        migrations.RemoveField(model_name="employee", name="emergency_contact_name"),
        migrations.RemoveField(model_name="employee", name="relationship"),
        migrations.RemoveField(model_name="employee", name="emergency_phone"),
        migrations.RemoveField(model_name="employee", name="emergency_address"),
        migrations.RemoveField(model_name="employee", name="role"),
        migrations.RemoveField(model_name="employee", name="permission_group"),
        migrations.RemoveField(model_name="employee", name="login_enabled"),
        migrations.RemoveField(model_name="employee", name="resignation_date"),
        migrations.RemoveField(model_name="employee", name="last_working_date"),
        migrations.RemoveField(model_name="employee", name="exit_reason"),
        migrations.RemoveField(model_name="employee", name="exit_notes"),
    ]

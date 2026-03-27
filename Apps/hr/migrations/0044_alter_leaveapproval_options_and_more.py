import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0043_alter_hire_status_alter_hiringplan_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveAccrual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accrual_date', models.DateField()),
                ('days_added', models.DecimalField(decimal_places=2, max_digits=7)),
                ('remarks', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(db_column='employee_id', on_delete=django.db.models.deletion.CASCADE, related_name='leave_accruals', to='hr.employee')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accruals', to='hr.leavetype')),
                ('policy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accruals', to='hr.leavepolicy')),
            ],
            options={
                'ordering': ['-accrual_date', '-created_at', '-id'],
                'constraints': [models.UniqueConstraint(fields=('employee', 'leave_type', 'policy', 'accrual_date'), name='unique_leave_accrual_employee_type_policy_date')],
            },
        ),
        migrations.CreateModel(
            name='LeaveBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('opening_balance', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('accrued', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('used', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('encashed', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(db_column='employee_id', on_delete=django.db.models.deletion.CASCADE, related_name='leave_balances', to='hr.employee')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balances', to='hr.leavetype')),
            ],
            options={
                'ordering': ['-year', 'employee__employee_id', 'leave_type__name'],
                'constraints': [models.UniqueConstraint(fields=('employee', 'leave_type', 'year'), name='unique_leave_balance_employee_type_year')],
            },
        ),
        migrations.CreateModel(
            name='LeaveLedger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('change_type', models.CharField(choices=[('opening', 'Opening'), ('accrual', 'Accrual'), ('leave_approved', 'Leave Approved'), ('leave_cancelled', 'Leave Cancelled'), ('leave_rejected', 'Leave Rejected'), ('encashment', 'Encashment'), ('carry_forward', 'Carry Forward'), ('adjustment', 'Adjustment'), ('compoff_earned', 'Comp Off Earned'), ('compoff_used', 'Comp Off Used')], max_length=50)),
                ('days', models.DecimalField(decimal_places=2, max_digits=7)),
                ('reference_type', models.CharField(blank=True, max_length=50)),
                ('reference_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('balance_after', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('remarks', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(db_column='employee_id', on_delete=django.db.models.deletion.CASCADE, related_name='leave_ledger_entries', to='hr.employee')),
                ('leave_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ledger_entries', to='hr.leavetype')),
            ],
            options={
                'ordering': ['-created_at', '-id'],
                'indexes': [models.Index(fields=['employee', 'leave_type', 'year'], name='hr_leaveled_employe_016856_idx'), models.Index(fields=['reference_type', 'reference_id'], name='hr_leaveled_referen_c802ce_idx')],
            },
        ),
    ]

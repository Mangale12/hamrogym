from django.db import models

from core.choices import SALARY_TYPE_CHOICES
from .employee import Employee


class EmployeePayroll(models.Model):
    SALARY_TYPE_CHOICES = SALARY_TYPE_CHOICES

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="payroll")
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPE_CHOICES, blank=True)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    allowance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    overtime_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_number = models.CharField(max_length=50, blank=True)

    class Meta:
        app_label = "hr"
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

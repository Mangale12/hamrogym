from django.db import models

from core.choices import PAYMENT_METHOD_CHOICES
from .employee import Employee


class EmployeeBank(models.Model):
    PAYMENT_METHOD_CHOICES = PAYMENT_METHOD_CHOICES

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="bank")
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)

    class Meta:
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

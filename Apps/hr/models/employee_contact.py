from django.db import models

from .employee import Employee


class EmployeeContact(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="contact")
    phone = models.CharField(max_length=30, blank=True)
    alternate_phone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

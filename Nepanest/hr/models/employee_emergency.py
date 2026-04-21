from django.db import models

from .employee import Employee


class EmployeeEmergency(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="emergency")
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    relationship = models.CharField(max_length=50, blank=True)
    emergency_phone = models.CharField(max_length=30, blank=True)
    emergency_address = models.TextField(blank=True)

    class Meta:
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

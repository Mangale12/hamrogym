from django.db import models

from .employee import Employee


class EmployeeAccess(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="access")
    role = models.CharField(max_length=100, blank=True)
    permission_group = models.CharField(max_length=100, blank=True)
    login_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

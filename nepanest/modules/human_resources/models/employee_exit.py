from django.db import models

from .employee import Employee


class EmployeeExit(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="exit")
    resignation_date = models.DateField(null=True, blank=True)
    last_working_date = models.DateField(null=True, blank=True)
    exit_reason = models.CharField(max_length=255, blank=True)
    exit_notes = models.TextField(blank=True)

    class Meta:
        app_label = "hr"
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

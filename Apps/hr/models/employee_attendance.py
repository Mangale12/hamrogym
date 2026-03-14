from django.db import models

from .employee import Employee


class EmployeeAttendance(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="attendance")
    attendance_required = models.BooleanField(default=True)
    leave_group = models.CharField(max_length=100, blank=True)
    weekly_off = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

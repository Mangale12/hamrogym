from django.db import models

from .employee import Employee


class EmployeeLegal(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="legal")
    citizenship_no = models.CharField(max_length=50, blank=True)
    passport_no = models.CharField(max_length=50, blank=True)
    pan_no = models.CharField(max_length=50, blank=True)
    social_security_no = models.CharField(max_length=50, blank=True)
    insurance_no = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

from django.db import models

from core.choices import WORK_LOCATION_CHOICES
from .employee import Employee


class EmployeeWork(models.Model):
    WORK_LOCATION_CHOICES = WORK_LOCATION_CHOICES

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="work")
    job_description = models.TextField(blank=True)
    work_location = models.CharField(max_length=20, choices=WORK_LOCATION_CHOICES, blank=True)
    work_email = models.EmailField(blank=True)
    joining_letter = models.FileField(upload_to="employee_documents/", null=True, blank=True)
    contract_file = models.FileField(upload_to="employee_documents/", null=True, blank=True)

    class Meta:
        app_label = "hr"
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

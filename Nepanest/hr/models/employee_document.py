from django.db import models

from .employee import Employee


class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=100, blank=True)
    doc_number = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to="employee_documents/", null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["doc_type", "doc_number"]

    def __str__(self) -> str:
        return f"{self.doc_type} {self.doc_number}".strip()

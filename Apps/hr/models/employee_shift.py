from django.db import models
from django.conf import settings

class EmployeeShift(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shifts")
    shift = models.ForeignKey("Shift", on_delete=models.CASCADE, related_name="employee_shifts")
    effective_from = models.DateTimeField(null=True, blank=True)
    effective_to = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee", "shift"]

    def __str__(self) -> str:
        return f"{self.employee} - {self.shift} ({self.effective_from} to {self.effective_to})"

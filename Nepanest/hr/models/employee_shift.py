from django.db import models


class EmployeeShift(models.Model):
    employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="shift_rotations")
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

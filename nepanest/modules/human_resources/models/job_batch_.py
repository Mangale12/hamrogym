from django.db import models
from core.choices import APPROVAL_STATUS_CHOICES
class JobBatches(models.Model):
    hiring_plan = models.ForeignKey("hr.HiringPlan", on_delete=models.CASCADE, null=True, blank=True, related_name="job_batches")
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True, null=False, blank=False)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, null=True, blank=True, related_name="job_batches")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="draft")
    approved_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

from django.conf import settings
from django.db import models

from core.choices import JOB_APPLICATION_STATUS_CHOICES


class JobApplication(models.Model):
    applicant = models.ForeignKey("Applicant", on_delete=models.CASCADE, related_name="job_applications")
    job_posting = models.ForeignKey("JobPosting", on_delete=models.CASCADE, related_name="job_applications")
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=JOB_APPLICATION_STATUS_CHOICES, default="applied", help_text="Current status of the job application")
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    source = models.CharField(max_length=100, blank=True, help_text="Source of the job application")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["-applied_date"]
        unique_together = ("applicant", "job_posting")

    def __str__(self) -> str:
        return f"{self.applicant} - {self.job_posting}"


class JobApplicationStatus(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="statuses")
    status = models.CharField(max_length=50, choices=JOB_APPLICATION_STATUS_CHOICES)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="job_application_status_changes")
    changed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.job_application} - {self.status}"

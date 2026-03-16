from django.conf import settings
from django.db import models

from core.choices import JOB_REQUISITION_STATUS_CHOICES, RECRUITMENT_REASON_CHOICES

class JobRequisition(models.Model):
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, null=True, blank=True, help_text="Branch for which the job is being requisitioned")
    department = models.ForeignKey("Department", on_delete=models.CASCADE, null=True, blank=True, help_text="Department for which the job is being requisitioned")
    designation = models.ForeignKey("Designation", on_delete=models.CASCADE, null=True, blank=True, help_text="Designation for which the job is being requisitioned")
    employment_type = models.ForeignKey("EmploymentType", on_delete=models.CASCADE, null=True, blank=True, help_text="Employment type for the job")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="requested_jobs")
    requisition_code = models.CharField(max_length=30, unique=True, blank=True)
    vacancies = models.PositiveIntegerField(default=1, help_text="Number of vacancies for the job requisition")
    job_title = models.CharField(max_length=150)
    job_description = models.TextField(blank=True)
    job_responsibilities = models.TextField(blank=True)
    required_skills = models.TextField(blank=True)
    required_experience = models.CharField(max_length=100, blank=True)
    education_requirement = models.TextField(blank=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    job_location = models.CharField(max_length=150, blank=True)
    priority = models.CharField(max_length=20)
    expected_joining_date = models.DateField(null=True, blank=True)
    recruitment_reason = models.CharField(max_length=30, choices=RECRUITMENT_REASON_CHOICES)
    status = models.CharField(max_length=20, choices=JOB_REQUISITION_STATUS_CHOICES, default="draft")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job Req #{self.id}"

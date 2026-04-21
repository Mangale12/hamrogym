from django.db import models
from django.conf import settings
from core.choices import APPROVAL_STATUS_CHOICES, PRIORITY_CHOICES
from core.mixins.fiscal_year import FiscalYearModelMixin
class JobRequisition(FiscalYearModelMixin, models.Model):
    batch = models.ForeignKey("JobBatches", on_delete=models.CASCADE, related_name="job_requisitions")
    requisition_code = models.CharField(max_length=100, unique=True)
    branch = models.ForeignKey("core.Branch", on_delete=models.CASCADE, null=True, blank=True, related_name="job_requisitions")
    department = models.ForeignKey("Department", on_delete=models.CASCADE, null=True, blank=True, related_name="job_requisitions")
    designation = models.ForeignKey("Designation", on_delete=models.CASCADE, null=True, blank=True, related_name="job_requisitions")
    employment_type = models.ForeignKey("EmploymentType", on_delete=models.CASCADE, null=True, blank=True, related_name="job_requisitions")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="job_requisitions")
    vacancies = models.PositiveIntegerField(default=1)
    job_title = models.CharField(max_length=250)
    job_description = models.TextField(blank=True, null=True)
    job_responsibilities = models.TextField(blank=True, null=True)
    required_skills = models.TextField(blank=True, null=True)
    required_experience = models.TextField(blank=True, null=True)
    education_requirement = models.TextField(blank=True, null=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_location = models.CharField(max_length=255, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    expected_joining_date = models.DateField(null=True, blank=True)
    recruitment_reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="draft")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["job_title"]

    def __str__(self) -> str:
        return self.job_title



class JobRequisitionApproval(FiscalYearModelMixin, models.Model):
    job_requisition = models.ManyToManyField(JobRequisition, related_name="approval")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="approved_requisitions")
    approve_level = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="level_1")
    approved_at = models.DateTimeField(auto_now_add=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="pending")
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-approved_at"]

    def __str__(self) -> str:
        return f"Approval for {self.job_requisition.job_title} by {self.approved_by}"
    



class JobRequisitionPosition(FiscalYearModelMixin, models.Model):
    job_requisition = models.ForeignKey(JobRequisition, on_delete=models.CASCADE, related_name="job_positions")
    position_title = models.CharField(max_length=250, null=True, blank=True)
    designation = models.ForeignKey("Designation", on_delete=models.CASCADE, null=True, blank=True, related_name="job_positions")
    position_description = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position_title"]

    def __str__(self) -> str:
        return self.position_title
    


class JobPositionSkill(models.Model):
    job_position = models.ForeignKey(JobRequisitionPosition, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey("JobSkill", on_delete=models.CASCADE, related_name="job_positions")
    skill_level = models.ForeignKey("SkillLevel", on_delete=models.CASCADE, null=True, blank=True, related_name="job_position_skills")
    class Meta:
        unique_together = ("job_position", "skill")

    def __str__(self) -> str:
        return f"{self.skill.name} ({self.skill_level.name})"
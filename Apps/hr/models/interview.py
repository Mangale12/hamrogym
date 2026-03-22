from django.db import models
from core.mixins.fiscal_year import FiscalYearModelMixin
from core.choices import INTERVIEW_MODE_CHOICES, INTERVIEW_STATUS_CHOICES
class Interview(FiscalYearModelMixin, models.Model):
    job_application = models.ForeignKey("JobApplication", on_delete=models.CASCADE)
    interview_stage = models.ForeignKey("InterviewStage", on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    location = models.CharField(max_length=255)
    mode = models.CharField(max_length=50, choices=INTERVIEW_MODE_CHOICES, default="in_person")
    status = models.CharField(max_length=50, choices=INTERVIEW_STATUS_CHOICES, default="scheduled")
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_at"]
        unique_together = ("job_application", "interview_stage")

    def __str__(self) -> str:
        return f"Interview for {self.job_application} - {self.interview_stage}"



class InterviewPanel(FiscalYearModelMixin, models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    panel_members = models.ManyToManyField("Employee", related_name="interview_panels")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("interview", "panelist")

    def __str__(self) -> str:
        return f"{self.panelist} - {self.role} for {self.interview}"
from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint

from core.mixins.fiscal_year import FiscalYearModelMixin
from core.choices import (
    INTERVIEW_FEEDBACK_RECOMMENDATIONS_CHOICES,
    INTERVIEW_MODE_CHOICES,
    INTERVIEW_STATUS_CHOICES,
)


class Interview(FiscalYearModelMixin, models.Model):
    job_application = models.ForeignKey(
        "JobApplication",
        on_delete=models.CASCADE,
        related_name="interviews",
    )
    interview_stage = models.ForeignKey(
        "InterviewStage",
        on_delete=models.CASCADE,
        related_name="interviews",
    )
    scheduled_at = models.DateTimeField()
    location = models.CharField(max_length=255)
    mode = models.CharField(max_length=50, choices=INTERVIEW_MODE_CHOICES, default="in_person")
    status = models.CharField(max_length=50, choices=INTERVIEW_STATUS_CHOICES, default="scheduled")
    sequence = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Auto-assigned stage order for this application's interview flow.",
    )
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["job_application", "sequence", "scheduled_at", "id"]
        constraints = [
            UniqueConstraint(
                fields=["job_application", "interview_stage"],
                name="unique_interview_stage_per_application",
            ),
            UniqueConstraint(
                fields=["job_application", "sequence"],
                name="unique_interview_sequence_per_application",
            ),
        ]

    def __str__(self) -> str:
        return f"Interview for {self.job_application} - {self.interview_stage}"

    def save(self, *args, **kwargs):
        if self.interview_stage_id:
            self.sequence = self.interview_stage.sequence
        super().save(*args, **kwargs)



class InterviewPanel(FiscalYearModelMixin, models.Model):
    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name="panel_members",
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="interview_panel",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["interview", "employee"],
                name="unique_employee_per_interview_panel",
            )
        ]

    def __str__(self) -> str:
        return f"{self.employee} for {self.interview}"


class InterviewFeedback(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="feedbacks")
    panel_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interview_feedbacks",
    )
    rating = models.PositiveIntegerField()
    comments = models.TextField(blank=True)
    recommendation = models.CharField(
        max_length=50,
        choices=INTERVIEW_FEEDBACK_RECOMMENDATIONS_CHOICES,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["interview", "panel_member"],
                name="unique_feedback_per_panel_member",
            )
        ]

    def __str__(self):
        return f"{self.interview} - {self.panel_member}"

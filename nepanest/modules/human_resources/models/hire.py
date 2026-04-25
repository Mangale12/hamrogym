from django.db import models

from core.choices import APPROVAL_STATUS_CHOICES


class Hire(models.Model):
    candidate = models.ForeignKey(
        "Applicant",
        on_delete=models.PROTECT,
        related_name="hires",
        db_column="candidate_id",
    )
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hires",
        db_column="employee_id",
    )
    job_offer = models.OneToOneField(
        "JobOffer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hire",
    )
    hire_date = models.DateField()
    designation = models.ForeignKey(
        "Designation",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hires",
        db_column="designation_id",
    )
    department = models.ForeignKey(
        "Department",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hires",
        db_column="department_id",
    )
    status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        db_table = "hr_hire"
        ordering = ["-hire_date", "-id"]

    def __str__(self) -> str:
        return f"{self.candidate} - {self.hire_date}"

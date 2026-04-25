from django.db import models
from core.choices import SCREENING_QUESTION_TYPE_CHOICES
class JobPosition(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey("Department", on_delete=models.RESTRICT, null=True, blank=True, help_text="Department associated with this job position")
    designation = models.ForeignKey("Designation", on_delete=models.RESTRICT, null=True, blank=True, help_text="Designation associated with this job position")
    job_category = models.ForeignKey("JobCategory", on_delete=models.RESTRICT, null=True, blank=True, help_text="Job category associated with this job position")
    vacancies = models.PositiveIntegerField(default=0, help_text="Number of vacancies for this job position")
    description = models.TextField(blank=True, help_text="Detailed description of the job position")
    employeement_type = models.ForeignKey("EmploymentType", on_delete=models.RESTRICT, null=True, blank=True, help_text="Employment type associated with this job position")
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Minimum salary for this job position")
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum salary for this job position")
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ScreeningQuestion(models.Model):
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name="screening_questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=SCREENING_QUESTION_TYPE_CHOICES)
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.question_text

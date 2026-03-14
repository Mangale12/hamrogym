from django.db import models


class JobPosting(models.Model):
    job_position = models.ForeignKey("job_position", on_delete=models.RESTRICT, null=False, blank=False)
    posting_date = models.DateField(null=False, blank=False)
    closing_date = models.DateField(null=False, blank=False)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["job_position"]
        db_table = "hr_job_posting"

    def __str__(self) -> str:
        return str(self.job_position)

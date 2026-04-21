from django.db import models

from core.mixins.fiscal_year import FiscalYearModelMixin


class JobPosting(FiscalYearModelMixin, models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    job_position = models.ForeignKey("JobPosition", on_delete=models.RESTRICT, null=False, blank=False)
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


class JobPostingChannelMap(FiscalYearModelMixin, models.Model):
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    job_posting_channel = models.ForeignKey("JobPostingChannel", on_delete=models.CASCADE)
    posted_url = models.URLField(max_length=255, blank=True, null=True)
    posted_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hr_job_posting_channel_map"

    def __str__(self) -> str:
        return f"{self.job_posting} - {self.job_posting_channel}"
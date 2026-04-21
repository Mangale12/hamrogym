from django.core.exceptions import ValidationError
from django.db import models

from core.choices import APPROVAL_STATUS_CHOICES
from core.mixins import FiscalYearModelMixin
from core.utils.upload_paths import build_upload_path
from core.validators import validate_file_extension, validate_file_size


JOB_OFFER_ATTACHMENT_ALLOWED_EXTENSIONS = (
    "pdf",
    "doc",
    "docx",
    "jpg",
    "jpeg",
    "png",
)
JOB_OFFER_ATTACHMENT_MAX_SIZE_MB = 5


def job_offer_attachment_file_path(instance, filename):
    return build_upload_path(
        base_dir="job_offer",
        instance=instance,
        filename=filename,
        field_name="attachments",
        name_attr="storage_name",
    )


def validate_job_offer_attachment(value):
    validate_file_extension(
        value,
        allowed_extensions=JOB_OFFER_ATTACHMENT_ALLOWED_EXTENSIONS,
    )
    validate_file_size(value, max_size_mb=JOB_OFFER_ATTACHMENT_MAX_SIZE_MB)


class JobOffer(FiscalYearModelMixin, models.Model):
    job_application = models.OneToOneField("JobApplication", on_delete=models.CASCADE)
    offer_date = models.DateField()
    salary_offered = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField()
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="pending")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["job_application"]
        verbose_name = "Job Offer"
        verbose_name_plural = "Job Offers"
        db_table = "hr_job_offer"

    def clean(self):
        super().clean()
        if self.offer_date and self.joining_date and self.joining_date < self.offer_date:
            raise ValidationError(
                {"joining_date": "Joining date cannot be earlier than the offer date."}
            )

    def __str__(self) -> str:
        return f"Job Offer for {self.job_application}"


class JobOfferAttachment(models.Model):
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(
        upload_to=job_offer_attachment_file_path,
        validators=[validate_job_offer_attachment],
    )
    document_type = models.CharField(max_length=100, null=True, blank=True, help_text="Type of the document (e.g., offer letter, contract)")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Offer Attachment"
        verbose_name_plural = "Job Offer Attachments"
        db_table = "hr_job_offer_attachment"

    @property
    def storage_name(self) -> str:
        job_offer_id = self.job_offer_id or "record"
        return f"job-offer-{job_offer_id}"

    def clean(self):
        super().clean()
        if self.file:
            validate_job_offer_attachment(self.file)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Attachment for {self.job_offer}"

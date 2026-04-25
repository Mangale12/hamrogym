from django.db import models

from nepanest.common.utils.upload_paths import build_upload_path

from core.choices import (
    GENDER_CHOICES,
    MARITAL_STATUS_CHOICES,
    APPLICANT_STATUS_CHOICES,
)


def _applicant_file_path(instance, filename, field_name):
    return build_upload_path(
        base_dir="applicant",
        instance=instance,
        filename=filename,
        field_name=field_name,
        name_attr="name",
    )


def applicant_cv_path(instance, filename):
    return _applicant_file_path(instance, filename, "cv")


def applicant_cover_letter_path(instance, filename):
    return _applicant_file_path(instance, filename, "cover_letter")


class Applicant(models.Model):
    name = models.CharField(max_length=255, help_text="Full name of the applicant")
    email = models.EmailField(null=True, help_text="Email address of the applicant")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number of the applicant")
    date_of_birth = models.DateField(null=True, help_text="Date of birth of the applicant")
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        help_text="Gender of the applicant",
    )
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        null=True,
        blank=True,
        help_text="Marital status of the applicant",
    )
    job_posting = models.ForeignKey("JobPosting", on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(blank=True, null=True, help_text="Address of the applicant")
    country = models.ForeignKey("core.Country", on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey("core.State", on_delete=models.SET_NULL, null=True, blank=True)
    city = models.CharField(max_length=255, blank=True, null=True, help_text="City of the applicant")
    cv = models.FileField(
        upload_to=applicant_cv_path,
        null=True,
        blank=True,
        help_text="CV of the applicant",
    )
    cover_letter = models.FileField(
        upload_to=applicant_cover_letter_path,
        null=True,
        blank=True,
        help_text="Cover letter of the applicant",
    )
    status = models.CharField(max_length=50, choices=APPLICANT_STATUS_CHOICES, default="pending", help_text="Application status")
    date = models.DateField(null=True, blank=True, help_text="Date of application")
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

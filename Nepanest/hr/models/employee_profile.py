from django.db import models

from core.choices import BLOOD_GROUP_CHOICES, GENDER_CHOICES, MARITAL_STATUS_CHOICES
from .employee import Employee


class EmployeeProfile(models.Model):
    GENDER_CHOICES = GENDER_CHOICES
    MARITAL_STATUS_CHOICES = MARITAL_STATUS_CHOICES
    BLOOD_GROUP_CHOICES = BLOOD_GROUP_CHOICES

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="profile")
    middle_name = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.ForeignKey(
        "core.Country",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hr_employee_profiles_nationality",
    )
    marital_status = models.CharField(
        max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True
    )
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, blank=True)
    profile_photo = models.ImageField(upload_to="employee_photos/", null=True, blank=True)

    class Meta:
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

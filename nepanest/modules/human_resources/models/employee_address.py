from django.db import models

from .employee import Employee


class EmployeeAddress(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="address")
    address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.ForeignKey(
        "core.State",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hr_employee_addresses_state",
    )
    country = models.ForeignKey(
        "core.Country",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hr_employee_addresses_country",
    )
    zip_code = models.CharField(max_length=20, blank=True)

    class Meta:
        app_label = "hr"
        ordering = ["employee__employee_id"]

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    def __str__(self) -> str:
        return self.employee.full_name or self.employee_id

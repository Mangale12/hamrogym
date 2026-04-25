from django.db import models

from core.choices import WEEKDAY_CHOICES


class HolidayCalendar(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["-year", "name"]
        constraints = [
            models.UniqueConstraint(fields=["name", "year"], name="unique_holiday_calendar_name_year"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.year})"


class Holiday(models.Model):
    holiday_calendar = models.ForeignKey(
        HolidayCalendar,
        on_delete=models.CASCADE,
        related_name="holidays",
    )
    name = models.CharField(max_length=120)
    date = models.DateField()
    is_optional = models.BooleanField(default=False)
    is_half_day = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["date", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["holiday_calendar", "date", "name"],
                name="unique_holiday_calendar_date_name",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.date:%Y-%m-%d}"


class WeeklyOffRule(models.Model):
    holiday_calendar = models.ForeignKey(
        HolidayCalendar,
        on_delete=models.CASCADE,
        related_name="weekly_off_rules",
    )
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["weekday"]
        constraints = [
            models.UniqueConstraint(
                fields=["holiday_calendar", "weekday"],
                name="unique_holiday_calendar_weekday",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.holiday_calendar} - {self.get_weekday_display()}"

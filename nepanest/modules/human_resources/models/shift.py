from django.db import models

class Shift(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, help_text="Optional name for the shift (e.g., 'Morning Shift', 'Evening Shift')")
    code = models.CharField(max_length=100, null=True, blank=True, help_text="Optional code for the shift (e.g., 'MOR', 'EVE')")
    start_time = models.TimeField(blank=True)
    end_time = models.TimeField(blank=True)
    break_start_time = models.TimeField(blank=True)
    break_end_time = models.TimeField(blank=True)
    grace_start_time = models.TimeField(blank=True)
    grace_end_time = models.TimeField(blank=True)
    is_active = models.BooleanField(default=True)
    break_duration = models.PositiveIntegerField(help_text="Break duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name or self.code or 'Shift'} ({self.start_time} - {self.end_time})"

from django.core.exceptions import ValidationError
from django.db import models, transaction


class FiscalYear(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": "End date must be after start date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.is_current:
                type(self).objects.exclude(pk=self.pk).filter(is_current=True).update(is_current=False)


class Currency(models.Model):
    code = models.CharField(
        max_length=155,
        unique=True,
        blank=False,
        help_text="Enter the currency code (e.g., USD, EUR)",
    )
    name = models.CharField(
        max_length=100,
        blank=False,
        help_text="Enter the currency name",
    )
    symbol = models.CharField(
        max_length=10,
        blank=False,
        help_text="Enter the currency symbol",
    )
    created_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"

    def __str__(self):
        return f"{self.name} ({self.code})"

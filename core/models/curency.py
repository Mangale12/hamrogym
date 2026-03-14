from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=155, unique=True, blank=False, help_text="Enter the currency code (e.g., USD, EUR)")
    name = models.CharField(max_length=100, blank=False, help_text="Enter the currency name")
    symbol = models.CharField(max_length=10, blank=False, help_text="Enter the currency symbol")
    created_by = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

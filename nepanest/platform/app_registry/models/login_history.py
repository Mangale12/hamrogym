from django.db import models


class LoginHistory(models.Model):
    client = models.ForeignKey("app_registry.Client", on_delete=models.CASCADE, related_name="login_histories")
    user_name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    is_successful = models.BooleanField(default=True)
    fail_reason = models.CharField(max_length=255, blank=True)
    logged_in_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.client} - {self.user_name} - {self.created_at}"

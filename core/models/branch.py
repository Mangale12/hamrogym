from django.conf import settings
from django.db import models


class Branch(models.Model):
    organization = models.ForeignKey("core.Organization", on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="core_branches_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["organization__name", "name"]
        unique_together = ("organization", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.organization})"

from django.db import models


class AssetLocation(models.Model):
    name = models.CharField(max_length=200, unique=True)
    branch = models.ForeignKey("core.Branch", null=True, blank=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

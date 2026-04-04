from django.db import models


class AssetType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey("AssetCategory", on_delete=models.CASCADE)
    depreciation_applicable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

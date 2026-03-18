from django.db import models


class ErpEntity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    module = models.CharField(max_length=255, blank=True)
    app_label = models.CharField(max_length=255, blank=True)
    model_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "erp_entity"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

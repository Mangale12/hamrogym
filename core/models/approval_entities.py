from django.db import models


class ApprovalEntity(models.Model):
    erp_entity = models.ForeignKey("ErpEntity", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

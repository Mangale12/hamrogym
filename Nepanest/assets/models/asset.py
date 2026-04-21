from django.conf import settings
from django.db import models


class Asset(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    category = models.ForeignKey("AssetCategory", null=True, blank=True, on_delete=models.CASCADE)
    asset_type = models.ForeignKey("AssetType", null=True, blank=True, on_delete=models.CASCADE)
    brand = models.ForeignKey("core.Brand", null=True, blank=True, on_delete=models.CASCADE)
    model = models.CharField(max_length=100, null=True, blank=True)
    serial_number = models.CharField(max_length=100, null=True, blank=True, unique=True)
    bar_code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vendor = models.ForeignKey("AssetVendor", null=True, blank=True, on_delete=models.CASCADE)
    warranty_expiry_date = models.DateField(null=True, blank=True)
    use_full_life_months = models.IntegerField(null=True, blank=True)
    salvage_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    depreciation_start_date = models.DateField(null=True, blank=True)
    current_location = models.ForeignKey("core.Location", null=True, blank=True, on_delete=models.CASCADE)
    current_department = models.ForeignKey("hr.Department", null=True, blank=True, on_delete=models.CASCADE)
    current_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    status = models.ForeignKey("AssetStatus", null=True, blank=True, on_delete=models.CASCADE)
    condition = models.ForeignKey("AssetCondition", null=True, blank=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class AssetDocument(models.Model):
    asset = models.ForeignKey("Asset", on_delete=models.CASCADE)
    document_type = models.CharField(max_length=255, null=True, blank=True)
    file_path = models.FileField(upload_to="asset_documents/")
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"Document for {self.asset.name}"

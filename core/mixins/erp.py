from django.conf import settings
from django.db import models


class TimeStampedModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserAuditModelMixin(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_records",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated_records",
    )

    class Meta:
        abstract = True


class FiscalYearBranchModelMixin(models.Model): 
    fiscal_year = models.ForeignKey(
        "core.FiscalYear",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_fiscal_year_records",
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_branch_records",
    )

    class Meta:
        abstract = True

class OrganizationBranchModelMixin(models.Model):
    organization = models.ForeignKey(
        "core.Organization",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_organization_records",
    )
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_branch_records",
    )

    class Meta:
        abstract = True

class ActiveRemarksModelMixin(models.Model):
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)

    class Meta:
        abstract = True


class ERPBaseModel(
    TimeStampedModelMixin,
    UserAuditModelMixin,
    FiscalYearBranchModelMixin,
    ActiveRemarksModelMixin,
    OrganizationBranchModelMixin,
):
    class Meta:
        abstract = True

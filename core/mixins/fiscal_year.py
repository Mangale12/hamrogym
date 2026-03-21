from django.db import models


class FiscalYearModelMixin(models.Model):
    fiscal_year = models.ForeignKey(
        "core.FiscalYear",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Fiscal year",
    )

    class Meta:
        abstract = True

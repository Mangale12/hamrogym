from django.db import models
from nepanest.common.mixins.erp import ERPBaseModel

class MembershipExtension(ERPBaseModel):
    membership = models.ForeignKey(
        "hamrogym.MemberMembership",
        on_delete=models.PROTECT,
        related_name="extensions"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="membership_extensions"
    )

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self) -> str:
        return f"Extension for {self.membership} ({self.start_date} to {self.end_date})"

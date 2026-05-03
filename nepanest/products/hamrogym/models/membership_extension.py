from django.db import models
from nepanest.common.mixins.erp import ERPBaseModel


class MembershipExtension(ERPBaseModel):
    membership = models.ForeignKey(
        "hamrogym.MemberMembership",
        on_delete=models.PROTECT,
        related_name="extensions"
    )
    extra_days = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="membership_extensions",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"Extension for {self.membership} ({self.extra_days} day(s))"

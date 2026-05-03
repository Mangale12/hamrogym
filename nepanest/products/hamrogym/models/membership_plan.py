from django.db import models

from core.mixins import ERPBaseModel


class MembershipPlan(ERPBaseModel):
    
    PLAN_TYPE_CHOICES = [
        ('duration_based', 'Duration Based'),
        ('session_based', 'Session Based'),
        ('hybrid', 'Hybrid'),
    ]
    
    name = models.CharField(max_length=150)
    duration_days = models.PositiveIntegerField()
    session_limit = models.PositiveIntegerField(null=True, blank=True)
    access_type = models.ForeignKey(
        "hamrogym.AccessType",
        on_delete=models.PROTECT,
        related_name="membership_plans",
    )
    freeze_limit_days = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='duration_based')

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "branch"],
                name="unique_hamrogym_membership_plan_name_branch",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.access_type.name})"


class MembershipRestriction(ERPBaseModel):
    class RestrictionType(models.TextChoices):
        TIME = "time", "Time"
        DAY = "day", "Day"
        USAGE = "usage", "Usage"

    membership_plan = models.ForeignKey(
        "hamrogym.MembershipPlan",
        on_delete=models.CASCADE,
        related_name="restrictions",
    )
    restriction_type = models.CharField(max_length=20, choices=RestrictionType.choices)
    value = models.CharField(max_length=255)

    class Meta:
        ordering = ["restriction_type", "id"]

    def __str__(self) -> str:
        return f"{self.membership_plan.name} - {self.get_restriction_type_display()}: {self.value}"

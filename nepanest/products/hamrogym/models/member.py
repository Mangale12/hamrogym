from django.core.exceptions import ValidationError
from django.db import models

from core.mixins import ERPBaseModel
from core.models import Party


class MemberStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"


class Member(ERPBaseModel):
    party = models.OneToOneField(
        Party,
        on_delete=models.PROTECT,
        related_name="hamrogym_member",
    )
    member_code = models.CharField(max_length=30, unique=True, blank=True)
    join_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=MemberStatus.choices,
        default=MemberStatus.ACTIVE,
    )
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["member_code", "id"]

    def __str__(self) -> str:
        return f"{self.member_code or 'Member'} - {self.party}"

    def clean(self):
        super().clean()
        if self.party_id and self.party.category != "individual":
            raise ValidationError({"party": "Only individual parties can be linked as gym members."})

    def save(self, *args, **kwargs):
        if not self.member_code:
            self.member_code = self._generate_member_code()
        if self.branch_id and not self.organization_id:
            self.organization_id = self.branch.organization_id
        self.is_active = self.status == MemberStatus.ACTIVE
        super().save(*args, **kwargs)

    def _generate_member_code(self) -> str:
        branch_token = None
        if self.branch_id:
            branch_value = (self.branch.code or self.branch.name or "").strip().upper()
            alnum = "".join(char for char in branch_value if char.isalnum())
            branch_token = alnum[:6] or f"BR{self.branch_id}"
        else:
            branch_token = "GEN"

        prefix = f"MBR-{branch_token}-"
        existing_codes = (
            type(self).objects.filter(member_code__startswith=prefix)
            .values_list("member_code", flat=True)
        )
        next_number = 1
        for code in existing_codes:
            suffix = (code or "").replace(prefix, "", 1)
            if suffix.isdigit():
                next_number = max(next_number, int(suffix) + 1)
        return f"{prefix}{next_number:05d}"


class MemberProfile(models.Model):
    FITNESS_GOAL_CHOICES = (
        ("weight_loss", "Weight Loss"),
        ("muscle_gain", "Muscle Gain"),
        ("general_fitness", "General Fitness"),
        ("strength", "Strength"),
        ("rehabilitation", "Rehabilitation"),
    )

    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fitness_goal = models.CharField(max_length=30, choices=FITNESS_GOAL_CHOICES, blank=True)
    medical_conditions = models.TextField(blank=True)

    class Meta:
        ordering = ["member_id"]

    def __str__(self) -> str:
        return f"Profile for {self.member}"

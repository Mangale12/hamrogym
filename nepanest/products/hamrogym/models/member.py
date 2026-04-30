from django.core.exceptions import ValidationError
from django.db import models

from core.mixins import ERPBaseModel
from core.models import Party


class Member(ERPBaseModel):
    party = models.OneToOneField(
        Party,
        on_delete=models.PROTECT,
        related_name="hamrogym_member",
    )
    member_code = models.CharField(max_length=30, unique=True, blank=True)
    join_date = models.DateField()
    status = models.ForeignKey(
        "hamrogym.MemberStatus",
        on_delete=models.PROTECT,
        related_name="members",
        null=True,
        blank=True,
    )
    activity_level = models.ForeignKey(
        "hamrogym.ActivityLevel",
        on_delete=models.PROTECT,
        related_name="members",
        null=True,
        blank=True,
    )
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    body_fat_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    medical_conditions = models.TextField(blank=True)
    injuries = models.TextField(blank=True)
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
        self.is_active = bool(self.status and self.status.code == "active")
        super().save(*args, **kwargs)

    def get_status_display(self):
        return self.status.name if self.status_id else ""

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
    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fitness_goals = models.ManyToManyField(
        "hamrogym.FitnessGoal",
        related_name="member_profiles",
        blank=True,
    )
    medical_conditions = models.TextField(blank=True)

    class Meta:
        ordering = ["member_id"]

    def __str__(self) -> str:
        return f"Profile for {self.member}"


class MemberReferral(ERPBaseModel):
    referrer_member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="referrals_made",
    )
    referred_member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="referrals_received",
    )
    referral_date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-referral_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=("referrer_member", "referred_member"),
                name="unique_hamrogym_member_referral_pair",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.referrer_member} referred {self.referred_member}"

    def clean(self):
        super().clean()
        errors = {}
        if (
            self.referrer_member_id
            and self.referred_member_id
            and self.referrer_member_id == self.referred_member_id
        ):
            errors["referred_member"] = "A member cannot refer themselves."
        if (
            self.referrer_member_id
            and self.branch_id
            and self.referrer_member.branch_id
            and self.referrer_member.branch_id != self.branch_id
        ):
            errors["referrer_member"] = "Referrer member branch must match the referral branch."
        if (
            self.referred_member_id
            and self.branch_id
            and self.referred_member.branch_id
            and self.referred_member.branch_id != self.branch_id
        ):
            errors["referred_member"] = "Referred member branch must match the referral branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.branch_id and not self.organization_id:
            self.organization_id = self.branch.organization_id
        super().save(*args, **kwargs)


class MemberTagMap(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="tag_maps",
    )
    tag = models.ForeignKey(
        "hamrogym.MemberTag",
        on_delete=models.CASCADE,
        related_name="member_maps",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("member", "tag")

    def __str__(self) -> str:
        return f"{self.member} - {self.tag}"

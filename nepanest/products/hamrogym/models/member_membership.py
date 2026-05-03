from django.core.exceptions import ValidationError
from django.db import models

from core.mixins import (
    FiscalYearBranchModelMixin,
    OrganizationBranchModelMixin,
    TimeStampedModelMixin,
    UserAuditModelMixin,
)


class MemberMembership(
    TimeStampedModelMixin,
    UserAuditModelMixin,
    FiscalYearBranchModelMixin,
    OrganizationBranchModelMixin,
):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"

    class Source(models.TextChoices):
        MANUAL = "manual", "Manual"
        ONLINE = "online", "Online"
        RENEWAL = "renewal", "Renewal"
        UPGRADE = "upgrade", "Upgrade"

    member = models.ForeignKey(
        "hamrogym.Member",
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    membership_plan = models.ForeignKey(
        "hamrogym.MembershipPlan",
        on_delete=models.PROTECT,
        related_name="member_memberships",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_sessions = models.PositiveIntegerField(null=True, blank=True)
    used_sessions = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)
    notes = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self) -> str:
        return f"{self.member} - {self.membership_plan.name}"

    def clean(self):
        super().clean()
        errors = {}
        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors["end_date"] = "End date cannot be earlier than start date."
        if self.total_sessions is not None and self.used_sessions > self.total_sessions:
            errors["used_sessions"] = "Used sessions cannot exceed total sessions."
        if self.membership_plan_id and self.branch_id and self.membership_plan.branch_id and self.membership_plan.branch_id != self.branch_id:
            errors["membership_plan"] = "Membership plan branch must match the membership branch."
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            errors["member"] = "Member branch must match the membership branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.membership_plan_id and self.total_sessions is None:
            self.total_sessions = self.membership_plan.session_limit
        if self.branch_id and not self.organization_id:
            self.organization_id = self.branch.organization_id
        super().save(*args, **kwargs)

    @property
    def remaining_sessions(self):
        if self.total_sessions is None:
            return None
        return max(self.total_sessions - self.used_sessions, 0)


class MembershipFreeze(
    TimeStampedModelMixin,
    UserAuditModelMixin,
    FiscalYearBranchModelMixin,
    OrganizationBranchModelMixin,
):
    member = models.ForeignKey(
        "hamrogym.Member",
        on_delete=models.PROTECT,
        related_name="membership_freezes",
    )
    membership = models.ForeignKey(
        "hamrogym.MemberMembership",
        on_delete=models.PROTECT,
        related_name="freezes",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.PositiveIntegerField(default=0)
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="membership_freezes",
        null=True,
        blank=True
    )
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self) -> str:
        return f"{self.member} freeze ({self.start_date} to {self.end_date})"

    def clean(self):
        super().clean()
        errors = {}
        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors["end_date"] = "End date cannot be earlier than start date."
        if self.membership_id and self.member_id and self.membership.member_id != self.member_id:
            errors["membership"] = "Selected membership does not belong to this member."
        if (
            self.membership_id
            and self.start_date
            and self.end_date
            and self.membership.membership_plan.freeze_limit_days
        ):
            freeze_days = (self.end_date - self.start_date).days + 1
            if freeze_days > self.membership.membership_plan.freeze_limit_days:
                errors["end_date"] = (
                    f"Freeze cannot exceed {self.membership.membership_plan.freeze_limit_days} day(s) "
                    "for the selected membership plan."
                )
        if self.membership_id and self.branch_id and self.membership.branch_id and self.membership.branch_id != self.branch_id:
            errors["membership"] = "Membership branch must match the freeze branch."
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            errors["member"] = "Member branch must match the freeze branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.total_days = (self.end_date - self.start_date).days + 1
        if self.branch_id and not self.organization_id:
            self.organization_id = self.branch.organization_id
        super().save(*args, **kwargs)


class MembershipUpgrade(
    TimeStampedModelMixin,
    UserAuditModelMixin,
    FiscalYearBranchModelMixin,
    OrganizationBranchModelMixin,
):
    member = models.ForeignKey(
        "hamrogym.Member",
        on_delete=models.PROTECT,
        related_name="membership_upgrades",
    )
    old_membership = models.ForeignKey(
        "hamrogym.MemberMembership",
        on_delete=models.PROTECT,
        related_name="upgrades_from",
    )
    new_membership = models.ForeignKey(
        "hamrogym.MemberMembership",
        on_delete=models.PROTECT,
        related_name="upgrades_to",
    )
    upgrade_date = models.DateField()
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-upgrade_date", "-id"]

    def __str__(self) -> str:
        return f"{self.member} upgrade on {self.upgrade_date}"

    def clean(self):
        super().clean()
        errors = {}
        if self.old_membership_id and self.member_id and self.old_membership.member_id != self.member_id:
            errors["old_membership"] = "Old membership does not belong to this member."
        if self.new_membership_id and self.member_id and self.new_membership.member_id != self.member_id:
            errors["new_membership"] = "New membership does not belong to this member."
        if self.old_membership_id and self.new_membership_id and self.old_membership_id == self.new_membership_id:
            errors["new_membership"] = "New membership must be different from old membership."
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            errors["member"] = "Member branch must match the upgrade branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.branch_id and not self.organization_id:
            self.organization_id = self.branch.organization_id
        super().save(*args, **kwargs)



class MembershipUsageLog(FiscalYearBranchModelMixin,
    OrganizationBranchModelMixin,
    TimeStampedModelMixin,
    UserAuditModelMixin):
    membership = models.ForeignKey(
        "hamrogym.MemberMembership",
        on_delete=models.PROTECT,
        related_name="usage_logs",
        null=True,
        blank=True
    )
    party = models.ForeignKey(
        "core.Party",
        on_delete=models.PROTECT,
        related_name="membership_usage_logs",
        null=True,
        blank=True
    )
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    date = models.DateField()
    sessions = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date", "-id"]
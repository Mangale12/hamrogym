from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.mixins import ERPBaseModel


class AccessDevice(ERPBaseModel):
    class DeviceType(models.TextChoices):
        QR_SCANNER = "qr_scanner", "QR Scanner"
        BIOMETRIC = "biometric", "Biometric"
        RFID = "rfid", "RFID"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        MAINTENANCE = "maintenance", "Maintenance"

    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=30, choices=DeviceType.choices)
    location = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "branch"],
                name="unique_hamrogym_access_device_name_branch",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()})"


class AccessRule(ERPBaseModel):
    class RuleType(models.TextChoices):
        TIME_LIMIT = "time_limit", "Time Limit"
        DAILY_LIMIT = "daily_limit", "Daily Limit"
        DAY_RESTRICTION = "day_restriction", "Day Restriction"

    membership_plan = models.ForeignKey(
        "hamrogym.MembershipPlan",
        on_delete=models.PROTECT,
        related_name="access_rules",
    )
    rule_type = models.CharField(max_length=30, choices=RuleType.choices)
    time_range_start = models.TimeField(null=True, blank=True)
    time_range_end = models.TimeField(null=True, blank=True)
    allowed_days = models.CharField(max_length=100, blank=True)
    max_checkins_per_day = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["membership_plan__name", "rule_type", "id"]

    def __str__(self):
        return f"{self.membership_plan.name} - {self.get_rule_type_display()}"

    @property
    def allowed_days_list(self):
        return [day.strip() for day in self.allowed_days.split(",") if day.strip()]

    def clean(self):
        super().clean()
        errors = {}
        if self.membership_plan_id and self.branch_id and self.membership_plan.branch_id:
            if self.membership_plan.branch_id != self.branch_id:
                errors["membership_plan"] = "Membership plan branch must match the access rule branch."
        if self.rule_type == self.RuleType.TIME_LIMIT:
            if not self.time_range_start or not self.time_range_end:
                errors["time_range_start"] = "Start and end time are required for time limit rules."
            elif self.time_range_end <= self.time_range_start:
                errors["time_range_end"] = "End time must be later than start time."
        elif self.rule_type == self.RuleType.DAILY_LIMIT:
            if not self.max_checkins_per_day:
                errors["max_checkins_per_day"] = "Max check-ins per day is required for daily limit rules."
        elif self.rule_type == self.RuleType.DAY_RESTRICTION:
            if not self.allowed_days.strip():
                errors["allowed_days"] = "Allowed days are required for day restriction rules."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.membership_plan_id:
            if self.membership_plan.branch_id and not self.branch_id:
                self.branch = self.membership_plan.branch
            if self.membership_plan.organization_id and not self.organization_id:
                self.organization = self.membership_plan.organization
            if self.membership_plan.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.membership_plan.fiscal_year
        super().save(*args, **kwargs)


class MemberCheckin(ERPBaseModel):
    class CheckinType(models.TextChoices):
        GYM = "gym", "Gym"
        CLASS = "class", "Class"
        PT_SESSION = "pt_session", "PT Session"

    class Source(models.TextChoices):
        QR = "qr", "QR"
        BIOMETRIC = "biometric", "Biometric"
        MANUAL = "manual", "Manual"
        CARD = "card", "Card"

    member = models.ForeignKey(
        "hamrogym.Member",
        on_delete=models.PROTECT,
        related_name="checkins",
    )
    member_membership = models.ForeignKey(
        "hamrogym.MemberMembership",
        on_delete=models.PROTECT,
        related_name="checkins",
    )
    checkin_time = models.DateTimeField(default=timezone.now)
    checkin_type = models.CharField(max_length=20, choices=CheckinType.choices, default=CheckinType.GYM)
    checkout_time = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)
    device = models.ForeignKey(
        "hamrogym.AccessDevice",
        on_delete=models.PROTECT,
        related_name="checkins",
        null=True,
        blank=True,
    )
    is_valid = models.BooleanField(default=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-checkin_time", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["member"],
                condition=Q(checkout_time__isnull=True),
                name="unique_hamrogym_open_checkin_per_member",
            ),
        ]

    def __str__(self):
        return f"{self.member} - {self.checkin_time:%Y-%m-%d %H:%M:%S}"

    @property
    def duration_minutes(self):
        if not self.checkout_time or not self.checkin_time:
            return None
        seconds = (self.checkout_time - self.checkin_time).total_seconds()
        return max(int(seconds // 60), 0)

    def clean(self):
        super().clean()
        errors = {}
        if self.member_membership_id and self.member_id and self.member_membership.member_id != self.member_id:
            errors["member_membership"] = "Selected membership does not belong to this member."
        if self.checkout_time and self.checkin_time and self.checkout_time < self.checkin_time:
            errors["checkout_time"] = "Checkout time cannot be earlier than check-in time."
        if self.device_id and self.branch_id and self.device.branch_id and self.device.branch_id != self.branch_id:
            errors["device"] = "Device branch must match the check-in branch."
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            errors["member"] = "Member branch must match the check-in branch."
        if self.is_valid:
            self.rejection_reason = ""
        elif not self.rejection_reason.strip():
            errors["rejection_reason"] = "Rejection reason is required for invalid check-ins."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.member_membership_id:
            if self.member_membership.branch_id and not self.branch_id:
                self.branch = self.member_membership.branch
            if self.member_membership.organization_id and not self.organization_id:
                self.organization = self.member_membership.organization
            if self.member_membership.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member_membership.fiscal_year
        elif self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        super().save(*args, **kwargs)

    def mark_checkout(self, checkout_time=None, save=True):
        self.checkout_time = checkout_time or timezone.now()
        if save:
            self.full_clean()
            self.save(update_fields=["checkout_time", "updated_at", "updated_by"])
        return self.duration_minutes


class CheckinSession(ERPBaseModel):
    member_checkin = models.ForeignKey(
        "hamrogym.MemberCheckin",
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    total_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-start_time", "-id"]

    def __str__(self):
        return f"Session #{self.pk or 'new'} - {self.member_checkin}"

    def clean(self):
        super().clean()
        errors = {}
        if self.end_time and self.start_time and self.end_time < self.start_time:
            errors["end_time"] = "End time cannot be earlier than start time."
        if self.member_checkin_id and self.branch_id and self.member_checkin.branch_id:
            if self.member_checkin.branch_id != self.branch_id:
                errors["member_checkin"] = "Check-in branch must match the session branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            seconds = (self.end_time - self.start_time).total_seconds()
            self.total_minutes = max(int(seconds // 60), 0)
        if self.member_checkin_id:
            if self.member_checkin.branch_id and not self.branch_id:
                self.branch = self.member_checkin.branch
            if self.member_checkin.organization_id and not self.organization_id:
                self.organization = self.member_checkin.organization
            if self.member_checkin.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member_checkin.fiscal_year
        super().save(*args, **kwargs)


class AccessLog(ERPBaseModel):
    device = models.ForeignKey(
        "hamrogym.AccessDevice",
        on_delete=models.PROTECT,
        related_name="access_logs",
    )
    member = models.ForeignKey(
        "hamrogym.Member",
        on_delete=models.PROTECT,
        related_name="access_logs",
        null=True,
        blank=True,
    )
    scan_time = models.DateTimeField(default=timezone.now)
    raw_data = models.TextField()
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-scan_time", "-id"]

    def __str__(self):
        member_label = self.member.member_code if self.member_id else "Unknown member"
        return f"{self.device.name} - {member_label} - {self.scan_time:%Y-%m-%d %H:%M:%S}"

    def clean(self):
        super().clean()
        errors = {}
        if self.device_id and self.branch_id and self.device.branch_id and self.device.branch_id != self.branch_id:
            errors["device"] = "Device branch must match the access log branch."
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            errors["member"] = "Member branch must match the access log branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.device_id:
            if self.device.branch_id and not self.branch_id:
                self.branch = self.device.branch
            if self.device.organization_id and not self.organization_id:
                self.organization = self.device.organization
            if self.device.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.device.fiscal_year
        elif self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        super().save(*args, **kwargs)


class AccessViolation(ERPBaseModel):
    class ViolationType(models.TextChoices):
        EXPIRED_PLAN = "expired_plan", "Expired Plan"
        EXCESS_USAGE = "excess_usage", "Excess Usage"
        RESTRICTED_TIME = "restricted_time", "Restricted Time"

    member = models.ForeignKey(
        "hamrogym.Member",
        on_delete=models.PROTECT,
        related_name="access_violations",
    )
    membership = models.ForeignKey(
        "hamrogym.MemberMembership",
        on_delete=models.PROTECT,
        related_name="access_violations",
        null=True,
        blank=True,
    )
    violation_type = models.CharField(max_length=30, choices=ViolationType.choices)
    detected_at = models.DateTimeField(default=timezone.now)
    action_taken = models.TextField(blank=True)

    class Meta:
        ordering = ["-detected_at", "-id"]

    def __str__(self):
        return f"{self.member} - {self.get_violation_type_display()}"

    def clean(self):
        super().clean()
        errors = {}
        if self.membership_id and self.membership.member_id != self.member_id:
            errors["membership"] = "Selected membership does not belong to this member."
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            errors["member"] = "Member branch must match the access violation branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.membership_id:
            if self.membership.branch_id and not self.branch_id:
                self.branch = self.membership.branch
            if self.membership.organization_id and not self.organization_id:
                self.organization = self.membership.organization
            if self.membership.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.membership.fiscal_year
        elif self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        super().save(*args, **kwargs)


class DailyAttendanceSummary(ERPBaseModel):
    member = models.ForeignKey(
        "hamrogym.Member",
        on_delete=models.CASCADE,
        related_name="daily_attendance_summaries",
    )
    date = models.DateField()
    total_checkins = models.PositiveIntegerField(default=0)
    total_duration = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "date"],
                name="unique_hamrogym_daily_attendance_member_date",
            ),
        ]

    def __str__(self):
        return f"{self.member} - {self.date}"

    def clean(self):
        super().clean()
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            raise ValidationError({"member": "Member branch must match the attendance summary branch."})

    def save(self, *args, **kwargs):
        if self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        super().save(*args, **kwargs)

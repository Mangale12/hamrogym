from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.mixins.erp import ERPBaseModel


class Challenge(ERPBaseModel):
    class ChallengeType(models.TextChoices):
        ATTENDANCE = "attendance", "Attendance"
        WEIGHT_LOSS = "weight_loss", "Weight Loss"
        WORKOUT = "workout", "Workout"
        CARDIO = "cardio", "Cardio"
        CUSTOM = "custom", "Custom"

    class GoalUnit(models.TextChoices):
        KG = "kg", "KG"
        DAYS = "days", "Days"
        REPS = "reps", "Reps"
        MINUTES = "minutes", "Minutes"
        CHECKINS = "checkins", "Checkins"

    class ParticipationType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        GROUP = "group", "Group"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        BRANCH_ONLY = "branch_only", "Branch Only"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    challenge_type = models.CharField(max_length=20, choices=ChallengeType.choices)
    goal_target = models.DecimalField(max_digits=10, decimal_places=2)
    goal_unit = models.CharField(max_length=20, choices=GoalUnit.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    participation_type = models.CharField(max_length=20, choices=ParticipationType.choices)
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["-start_date", "title", "id"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        errors = {}
        if self.goal_target is not None and self.goal_target <= 0:
            errors["goal_target"] = "Goal target must be greater than zero."
        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors["end_date"] = "End date cannot be earlier than start date."
        if self.visibility == self.Visibility.BRANCH_ONLY and not self.branch_id:
            errors["branch"] = "Branch is required for branch-only challenges."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.branch_id and self.branch.organization_id and not self.organization_id:
            self.organization = self.branch.organization
        self.is_active = self.status == self.Status.ACTIVE
        super().save(*args, **kwargs)


class ChallengeParticipant(ERPBaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        DISQUALIFIED = "disqualified", "Disqualified"

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="participants")
    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="challenge_participants")
    joined_at = models.DateTimeField(default=timezone.now)
    current_progress = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    current_rank = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["challenge_id", "current_rank", "-current_progress", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["challenge", "member"],
                name="unique_hamrogym_challenge_participant",
            ),
        ]

    def __str__(self):
        return f"{self.member} - {self.challenge}"

    def clean(self):
        super().clean()
        errors = {}
        if self.current_progress is not None and self.current_progress < 0:
            errors["current_progress"] = "Current progress cannot be negative."
        if self.completion_percentage is not None and (
            self.completion_percentage < 0 or self.completion_percentage > 100
        ):
            errors["completion_percentage"] = "Completion percentage must be between 0 and 100."
        if self.challenge_id and self.member_id:
            if self.challenge.branch_id and self.member.branch_id and self.challenge.branch_id != self.member.branch_id:
                errors["member"] = "Member branch must match the challenge branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.challenge_id:
            if self.challenge.branch_id and not self.branch_id:
                self.branch = self.challenge.branch
            if self.challenge.organization_id and not self.organization_id:
                self.organization = self.challenge.organization
            if self.challenge.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.challenge.fiscal_year
        if self.challenge_id and self.challenge.goal_target:
            percent = (self.current_progress / self.challenge.goal_target) * 100
            self.completion_percentage = min(percent, 100)
        super().save(*args, **kwargs)


class ChallengeProgressLog(ERPBaseModel):
    class SourceType(models.TextChoices):
        MANUAL = "manual", "Manual"
        ATTENDANCE = "attendance", "Attendance"
        WORKOUT = "workout", "Workout"
        WEARABLE_DEVICE = "wearable_device", "Wearable Device"

    challenge_participant = models.ForeignKey(
        ChallengeParticipant,
        on_delete=models.CASCADE,
        related_name="progress_logs",
    )
    logged_at = models.DateTimeField(default=timezone.now)
    progress_value = models.DecimalField(max_digits=10, decimal_places=2)
    source_type = models.CharField(max_length=20, choices=SourceType.choices, default=SourceType.MANUAL)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-logged_at", "-id"]

    def __str__(self):
        return f"{self.challenge_participant} - {self.progress_value}"

    def clean(self):
        super().clean()
        if self.progress_value is not None and self.progress_value < 0:
            raise ValidationError({"progress_value": "Progress value cannot be negative."})

    def save(self, *args, **kwargs):
        participant = self.challenge_participant
        if participant.branch_id and not self.branch_id:
            self.branch = participant.branch
        if participant.organization_id and not self.organization_id:
            self.organization = participant.organization
        if participant.fiscal_year_id and not self.fiscal_year_id:
            self.fiscal_year = participant.fiscal_year
        super().save(*args, **kwargs)
        if participant.current_progress != self.progress_value:
            participant.current_progress = self.progress_value
            participant.save(update_fields=["current_progress", "completion_percentage"])


class Leaderboard(ERPBaseModel):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="leaderboards")
    generated_at = models.DateTimeField(default=timezone.now)
    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="leaderboard_snapshots")
    rank_position = models.PositiveIntegerField()
    score_value = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-generated_at", "rank_position", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["challenge", "generated_at", "member"],
                name="unique_hamrogym_leaderboard_snapshot_member",
            ),
        ]

    def __str__(self):
        return f"{self.challenge} - {self.member} - Rank {self.rank_position}"

    def clean(self):
        super().clean()
        errors = {}
        if self.rank_position < 1:
            errors["rank_position"] = "Rank position must be at least 1."
        if self.score_value is not None and self.score_value < 0:
            errors["score_value"] = "Score value cannot be negative."
        if self.challenge_id and self.member_id:
            if self.challenge.branch_id and self.member.branch_id and self.challenge.branch_id != self.member.branch_id:
                errors["member"] = "Member branch must match the challenge branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.challenge_id:
            if self.challenge.branch_id and not self.branch_id:
                self.branch = self.challenge.branch
            if self.challenge.organization_id and not self.organization_id:
                self.organization = self.challenge.organization
            if self.challenge.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.challenge.fiscal_year
        super().save(*args, **kwargs)


class AchievementBadge(ERPBaseModel):
    class BadgeType(models.TextChoices):
        ATTENDANCE = "attendance", "Attendance"
        WORKOUT = "workout", "Workout"
        CHALLENGE = "challenge", "Challenge"
        MILESTONE = "milestone", "Milestone"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=255, blank=True)
    badge_type = models.CharField(max_length=20, choices=BadgeType.choices)
    criteria_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.criteria_value is not None and self.criteria_value <= 0:
            raise ValidationError({"criteria_value": "Criteria value must be greater than zero."})

    def save(self, *args, **kwargs):
        self.is_active = self.status == self.Status.ACTIVE
        super().save(*args, **kwargs)


class MemberBadge(ERPBaseModel):
    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="badges")
    achievement_badge = models.ForeignKey(
        AchievementBadge,
        on_delete=models.CASCADE,
        related_name="member_badges",
    )
    awarded_at = models.DateTimeField(default=timezone.now)
    source_reference_type = models.CharField(max_length=50, blank=True)
    source_reference_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-awarded_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "achievement_badge"],
                name="unique_hamrogym_member_badge",
            ),
        ]

    def __str__(self):
        return f"{self.member} - {self.achievement_badge}"

    def clean(self):
        super().clean()
        if self.member_id and self.achievement_badge_id:
            if self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
                raise ValidationError({"member": "Member branch must match the badge branch."})

    def save(self, *args, **kwargs):
        if self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        super().save(*args, **kwargs)


class MemberStreak(ERPBaseModel):
    class StreakType(models.TextChoices):
        ATTENDANCE = "attendance", "Attendance"
        WORKOUT = "workout", "Workout"
        DIET = "diet", "Diet"

    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="streaks")
    streak_type = models.CharField(max_length=20, choices=StreakType.choices)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["member_id", "streak_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "streak_type"],
                name="unique_hamrogym_member_streak_type",
            ),
        ]

    def __str__(self):
        return f"{self.member} - {self.get_streak_type_display()}"

    def clean(self):
        super().clean()
        errors = {}
        if self.longest_streak < self.current_streak:
            errors["longest_streak"] = "Longest streak cannot be less than current streak."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        super().save(*args, **kwargs)


class Reward(ERPBaseModel):
    class RewardType(models.TextChoices):
        PHYSICAL = "physical", "Physical"
        DISCOUNT = "discount", "Discount"
        DIGITAL = "digital", "Digital"
        MEMBERSHIP_EXTENSION = "membership_extension", "Membership Extension"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=150, unique=True)
    reward_type = models.CharField(max_length=30, choices=RewardType.choices)
    description = models.TextField(blank=True)
    points_required = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.points_required is not None and self.points_required < 0:
            raise ValidationError({"points_required": "Points required cannot be negative."})

    def save(self, *args, **kwargs):
        self.is_active = self.status == self.Status.ACTIVE
        super().save(*args, **kwargs)


class MemberReward(ERPBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="rewards")
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name="member_rewards")
    redeemed_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["-redeemed_at", "-id"]

    def __str__(self):
        return f"{self.member} - {self.reward}"

    def clean(self):
        super().clean()
        if self.member_id and self.reward_id:
            if self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
                raise ValidationError({"member": "Member branch must match the reward branch."})

    def save(self, *args, **kwargs):
        if self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        super().save(*args, **kwargs)

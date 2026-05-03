from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.mixins import ERPBaseModel


class Trainer(ERPBaseModel):
    class Specialization(models.TextChoices):
        STRENGTH = "strength", "Strength"
        CARDIO = "cardio", "Cardio"
        YOGA = "yoga", "Yoga"
        REHAB = "rehab", "Rehab"
        CROSSFIT = "crossfit", "Crossfit"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    employee = models.OneToOneField(
        "hr.Employee",
        on_delete=models.PROTECT,
        related_name="hamrogym_trainer",
    )
    specialization = models.CharField(max_length=20, choices=Specialization.choices)
    experience_years = models.PositiveIntegerField(default=0)
    certification_details = models.TextField(blank=True)
    max_sessions_per_day = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["employee__employee_id", "id"]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.employee.full_name or 'Trainer'}"

    def clean(self):
        super().clean()
        errors = {}
        if self.rating is not None and (self.rating < 0 or self.rating > 5):
            errors["rating"] = "Rating must be between 0 and 5."
        if self.employee_id and self.branch_id and self.employee.branch_id and self.employee.branch_id != self.branch_id:
            errors["employee"] = "Employee branch must match the trainer branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.employee_id:
            if self.employee.branch_id and not self.branch_id:
                self.branch = self.employee.branch
            if self.employee.organization_id and not self.organization_id:
                self.organization = self.employee.organization
        self.is_active = self.status == self.Status.ACTIVE
        super().save(*args, **kwargs)


class TrainerAvailability(ERPBaseModel):
    class DayOfWeek(models.TextChoices):
        MONDAY = "monday", "Monday"
        TUESDAY = "tuesday", "Tuesday"
        WEDNESDAY = "wednesday", "Wednesday"
        THURSDAY = "thursday", "Thursday"
        FRIDAY = "friday", "Friday"
        SATURDAY = "saturday", "Saturday"
        SUNDAY = "sunday", "Sunday"

    trainer = models.ForeignKey(
        "hamrogym.Trainer",
        on_delete=models.CASCADE,
        related_name="availabilities",
    )
    day_of_week = models.CharField(max_length=10, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["trainer__employee__employee_id", "day_of_week", "start_time", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["trainer", "day_of_week", "start_time", "end_time"],
                name="unique_hamrogym_trainer_availability_slot",
            ),
        ]

    def __str__(self):
        return f"{self.trainer} - {self.get_day_of_week_display()} {self.start_time} to {self.end_time}"

    def clean(self):
        super().clean()
        errors = {}
        if self.end_time <= self.start_time:
            errors["end_time"] = "End time must be later than start time."
        if self.trainer_id and self.branch_id and self.trainer.branch_id and self.trainer.branch_id != self.branch_id:
            errors["trainer"] = "Trainer branch must match the availability branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.trainer_id:
            if self.trainer.branch_id and not self.branch_id:
                self.branch = self.trainer.branch
            if self.trainer.organization_id and not self.organization_id:
                self.organization = self.trainer.organization
            if self.trainer.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.trainer.fiscal_year
        super().save(*args, **kwargs)


class TrainerTimeOff(ERPBaseModel):
    trainer = models.ForeignKey(
        "hamrogym.Trainer",
        on_delete=models.CASCADE,
        related_name="time_off_entries",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return f"{self.trainer} time off ({self.start_date} to {self.end_date})"

    def clean(self):
        super().clean()
        errors = {}
        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["end_date"] = "End date cannot be earlier than start date."
        if self.trainer_id and self.branch_id and self.trainer.branch_id and self.trainer.branch_id != self.branch_id:
            errors["trainer"] = "Trainer branch must match the time-off branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.trainer_id:
            if self.trainer.branch_id and not self.branch_id:
                self.branch = self.trainer.branch
            if self.trainer.organization_id and not self.organization_id:
                self.organization = self.trainer.organization
            if self.trainer.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.trainer.fiscal_year
        super().save(*args, **kwargs)


class PTSessionPackage(ERPBaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=120)
    total_sessions = models.PositiveIntegerField()
    validity_days = models.PositiveIntegerField()
    session_duration_minutes = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "branch"],
                name="unique_hamrogym_pt_session_package_name_branch",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        errors = {}
        if self.total_sessions < 1:
            errors["total_sessions"] = "Total sessions must be at least 1."
        if self.validity_days < 1:
            errors["validity_days"] = "Validity days must be at least 1."
        if self.session_duration_minutes < 1:
            errors["session_duration_minutes"] = "Session duration must be at least 1 minute."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.is_active = self.status == self.Status.ACTIVE
        super().save(*args, **kwargs)


class MemberPTPackage(ERPBaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        COMPLETED = "completed", "Completed"

    member = models.ForeignKey(
        "hamrogym.Member",
        on_delete=models.PROTECT,
        related_name="pt_packages",
    )
    pt_session_package = models.ForeignKey(
        "hamrogym.PTSessionPackage",
        on_delete=models.PROTECT,
        related_name="member_packages",
    )
    total_sessions = models.PositiveIntegerField()
    used_sessions = models.PositiveIntegerField(default=0)
    remaining_sessions = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return f"{self.member} - {self.pt_session_package.name}"

    def clean(self):
        super().clean()
        errors = {}
        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["end_date"] = "End date cannot be earlier than start date."
        if self.used_sessions > self.total_sessions:
            errors["used_sessions"] = "Used sessions cannot exceed total sessions."
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            errors["member"] = "Member branch must match the package branch."
        if (
            self.pt_session_package_id
            and self.branch_id
            and self.pt_session_package.branch_id
            and self.pt_session_package.branch_id != self.branch_id
        ):
            errors["pt_session_package"] = "PT package branch must match the member PT package branch."
        if errors:
            raise ValidationError(errors)

    def _derive_status(self):
        today = timezone.localdate()
        if self.remaining_sessions <= 0:
            return self.Status.COMPLETED
        if self.end_date and self.end_date < today:
            return self.Status.EXPIRED
        return self.Status.ACTIVE

    def refresh_usage(self, save=True):
        completed_sessions = self.pt_sessions.filter(status=PTSession.Status.COMPLETED).count() if self.pk else 0
        self.used_sessions = completed_sessions
        self.remaining_sessions = max(self.total_sessions - self.used_sessions, 0)
        self.status = self._derive_status()
        self.is_active = self.status == self.Status.ACTIVE
        if save and self.pk:
            type(self).objects.filter(pk=self.pk).update(
                used_sessions=self.used_sessions,
                remaining_sessions=self.remaining_sessions,
                status=self.status,
                is_active=self.is_active,
                updated_at=timezone.now(),
            )
        return self.remaining_sessions

    def save(self, *args, **kwargs):
        if self.pt_session_package_id and not self.total_sessions:
            self.total_sessions = self.pt_session_package.total_sessions
        if self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        if self.pt_session_package_id:
            if self.pt_session_package.branch_id and not self.branch_id:
                self.branch = self.pt_session_package.branch
            if self.pt_session_package.organization_id and not self.organization_id:
                self.organization = self.pt_session_package.organization
            if self.pt_session_package.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.pt_session_package.fiscal_year
        self.remaining_sessions = max((self.total_sessions or 0) - (self.used_sessions or 0), 0)
        self.status = self._derive_status()
        self.is_active = self.status == self.Status.ACTIVE
        super().save(*args, **kwargs)


class PTSession(ERPBaseModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    member = models.ForeignKey(
        "hamrogym.Member",
        on_delete=models.PROTECT,
        related_name="pt_sessions",
    )
    trainer = models.ForeignKey(
        "hamrogym.Trainer",
        on_delete=models.PROTECT,
        related_name="pt_sessions",
    )
    member_pt_package = models.ForeignKey(
        "hamrogym.MemberPTPackage",
        on_delete=models.PROTECT,
        related_name="pt_sessions",
    )
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    checkin = models.ForeignKey(
        "hamrogym.MemberCheckin",
        on_delete=models.PROTECT,
        related_name="pt_sessions",
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-session_date", "start_time", "-id"]

    def __str__(self):
        return f"{self.member} with {self.trainer} on {self.session_date}"

    @property
    def duration_minutes(self):
        session_start = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute, seconds=self.start_time.second)
        session_end = timedelta(hours=self.end_time.hour, minutes=self.end_time.minute, seconds=self.end_time.second)
        return max(int((session_end - session_start).total_seconds() // 60), 0)

    def _validate_trainer_availability(self, errors):
        if not self.trainer_id or not self.session_date or not self.start_time or not self.end_time:
            return
        weekday = self.session_date.strftime("%A").lower()
        is_available = self.trainer.availabilities.filter(
            day_of_week=weekday,
            start_time__lte=self.start_time,
            end_time__gte=self.end_time,
            is_available=True,
        ).exists()
        if not is_available:
            errors["trainer"] = "Trainer is not available during the selected session slot."
        if self.trainer.time_off_entries.filter(
            start_date__lte=self.session_date,
            end_date__gte=self.session_date,
        ).exists():
            errors["session_date"] = "Trainer is on time off for the selected session date."

    def _validate_overlap(self, errors):
        if not self.session_date or not self.start_time or not self.end_time:
            return
        active_statuses = [self.Status.SCHEDULED, self.Status.COMPLETED]
        trainer_overlap = type(self).objects.filter(
            trainer=self.trainer,
            session_date=self.session_date,
            status__in=active_statuses,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        member_overlap = type(self).objects.filter(
            member=self.member,
            session_date=self.session_date,
            status__in=active_statuses,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        if self.pk:
            trainer_overlap = trainer_overlap.exclude(pk=self.pk)
            member_overlap = member_overlap.exclude(pk=self.pk)
        if trainer_overlap.exists():
            errors["trainer"] = "Trainer already has another PT session in this time range."
        if member_overlap.exists():
            errors["member"] = "Member already has another PT session in this time range."

    def clean(self):
        super().clean()
        errors = {}
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            errors["end_time"] = "End time must be later than start time."
        if self.member_pt_package_id and self.member_id and self.member_pt_package.member_id != self.member_id:
            errors["member_pt_package"] = "Selected member PT package does not belong to this member."
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            errors["member"] = "Member branch must match the PT session branch."
        if self.trainer_id and self.branch_id and self.trainer.branch_id and self.trainer.branch_id != self.branch_id:
            errors["trainer"] = "Trainer branch must match the PT session branch."
        if self.checkin_id and self.member_id and self.checkin.member_id != self.member_id:
            errors["checkin"] = "Selected member check-in does not belong to this member."
        if self.member_pt_package_id:
            package = self.member_pt_package
            if package.start_date and self.session_date and self.session_date < package.start_date:
                errors["session_date"] = "Session date cannot be earlier than package start date."
            if package.end_date and self.session_date and self.session_date > package.end_date:
                errors["session_date"] = "Session date cannot be later than package end date."
            if package.status != MemberPTPackage.Status.ACTIVE and self.status in {self.Status.SCHEDULED, self.Status.COMPLETED}:
                errors["member_pt_package"] = "Only active member PT packages can be scheduled or completed."
        if self.trainer_id and self.trainer.status != Trainer.Status.ACTIVE:
            errors["trainer"] = "Inactive trainers cannot be assigned to PT sessions."
        if self.status in {self.Status.SCHEDULED, self.Status.COMPLETED}:
            self._validate_trainer_availability(errors)
            self._validate_overlap(errors)
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.member_pt_package_id:
            if self.member_pt_package.branch_id and not self.branch_id:
                self.branch = self.member_pt_package.branch
            if self.member_pt_package.organization_id and not self.organization_id:
                self.organization = self.member_pt_package.organization
            if self.member_pt_package.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member_pt_package.fiscal_year
        elif self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        super().save(*args, **kwargs)
        if self.member_pt_package_id:
            self.member_pt_package.refresh_usage(save=True)

    def delete(self, *args, **kwargs):
        package = self.member_pt_package if self.member_pt_package_id else None
        result = super().delete(*args, **kwargs)
        if package and package.pk:
            package.refresh_usage(save=True)
        return result


class PTSessionLog(ERPBaseModel):
    pt_session = models.OneToOneField(
        "hamrogym.PTSession",
        on_delete=models.CASCADE,
        related_name="execution_log",
    )
    actual_start_time = models.DateTimeField()
    actual_end_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=0)
    trainer_notes = models.TextField(blank=True)
    member_feedback = models.TextField(blank=True)

    class Meta:
        ordering = ["-actual_start_time", "-id"]

    def __str__(self):
        return f"Execution log for {self.pt_session}"

    def clean(self):
        super().clean()
        errors = {}
        if self.actual_end_time and self.actual_start_time and self.actual_end_time < self.actual_start_time:
            errors["actual_end_time"] = "Actual end time cannot be earlier than actual start time."
        if self.pt_session_id and self.branch_id and self.pt_session.branch_id and self.pt_session.branch_id != self.branch_id:
            errors["pt_session"] = "PT session branch must match the execution log branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.actual_end_time and self.actual_start_time:
            seconds = (self.actual_end_time - self.actual_start_time).total_seconds()
            self.duration_minutes = max(int(seconds // 60), 0)
        if self.pt_session_id:
            if self.pt_session.branch_id and not self.branch_id:
                self.branch = self.pt_session.branch
            if self.pt_session.organization_id and not self.organization_id:
                self.organization = self.pt_session.organization
            if self.pt_session.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.pt_session.fiscal_year
        super().save(*args, **kwargs)
        if self.pt_session_id and self.pt_session.status != PTSession.Status.COMPLETED:
            self.pt_session.status = PTSession.Status.COMPLETED
            self.pt_session.save(update_fields=["status", "updated_at"])


class PTSessionReschedule(ERPBaseModel):
    pt_session = models.ForeignKey(
        "hamrogym.PTSession",
        on_delete=models.CASCADE,
        related_name="reschedules",
    )
    old_date = models.DateField()
    old_start_time = models.TimeField()
    new_date = models.DateField()
    new_start_time = models.TimeField()
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Reschedule for {self.pt_session}"

    def clean(self):
        super().clean()
        errors = {}
        if self.pt_session_id and self.old_date and self.old_date != self.pt_session.session_date:
            errors["old_date"] = "Old date must match the session's current scheduled date."
        if self.pt_session_id and self.old_start_time and self.old_start_time != self.pt_session.start_time:
            errors["old_start_time"] = "Old start time must match the session's current scheduled start time."
        if self.pt_session_id and self.branch_id and self.pt_session.branch_id and self.pt_session.branch_id != self.branch_id:
            errors["pt_session"] = "PT session branch must match the reschedule branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.pt_session_id:
            if self.pt_session.branch_id and not self.branch_id:
                self.branch = self.pt_session.branch
            if self.pt_session.organization_id and not self.organization_id:
                self.organization = self.pt_session.organization
            if self.pt_session.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.pt_session.fiscal_year
        super().save(*args, **kwargs)

        if self.pt_session_id:
            session = self.pt_session
            duration = session.duration_minutes
            session.session_date = self.new_date
            session.start_time = self.new_start_time
            new_end_datetime = datetime.combine(self.new_date, self.new_start_time) + timedelta(minutes=duration)
            session.end_time = new_end_datetime.time()
            session.full_clean()
            session.save(update_fields=["session_date", "start_time", "end_time", "updated_at"])


class PTSessionCancellation(ERPBaseModel):
    class CancelledBy(models.TextChoices):
        MEMBER = "member", "Member"
        TRAINER = "trainer", "Trainer"
        ADMIN = "admin", "Admin"

    pt_session = models.OneToOneField(
        "hamrogym.PTSession",
        on_delete=models.CASCADE,
        related_name="cancellation",
    )
    cancelled_by = models.CharField(max_length=20, choices=CancelledBy.choices)
    reason = models.TextField(blank=True)
    cancellation_time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-cancellation_time", "-id"]

    def __str__(self):
        return f"Cancellation for {self.pt_session}"

    def clean(self):
        super().clean()
        errors = {}
        if self.pt_session_id and self.branch_id and self.pt_session.branch_id and self.pt_session.branch_id != self.branch_id:
            errors["pt_session"] = "PT session branch must match the cancellation branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.pt_session_id:
            if self.pt_session.branch_id and not self.branch_id:
                self.branch = self.pt_session.branch
            if self.pt_session.organization_id and not self.organization_id:
                self.organization = self.pt_session.organization
            if self.pt_session.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.pt_session.fiscal_year
        super().save(*args, **kwargs)
        if self.pt_session_id and self.pt_session.status != PTSession.Status.CANCELLED:
            self.pt_session.status = PTSession.Status.CANCELLED
            self.pt_session.save(update_fields=["status", "updated_at"])


class TrainerPerformance(ERPBaseModel):
    trainer = models.ForeignKey(
        "hamrogym.Trainer",
        on_delete=models.CASCADE,
        related_name="performance_rows",
    )
    date = models.DateField()
    total_sessions = models.PositiveIntegerField(default=0)
    completed_sessions = models.PositiveIntegerField(default=0)
    cancelled_sessions = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date", "trainer__employee__employee_id", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["trainer", "date"],
                name="unique_hamrogym_trainer_performance_date",
            ),
        ]

    def __str__(self):
        return f"{self.trainer} - {self.date}"

    def clean(self):
        super().clean()
        errors = {}
        if self.completed_sessions > self.total_sessions:
            errors["completed_sessions"] = "Completed sessions cannot exceed total sessions."
        if self.cancelled_sessions > self.total_sessions:
            errors["cancelled_sessions"] = "Cancelled sessions cannot exceed total sessions."
        if self.trainer_id and self.branch_id and self.trainer.branch_id and self.trainer.branch_id != self.branch_id:
            errors["trainer"] = "Trainer branch must match the performance branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.trainer_id:
            if self.trainer.branch_id and not self.branch_id:
                self.branch = self.trainer.branch
            if self.trainer.organization_id and not self.organization_id:
                self.organization = self.trainer.organization
            if self.trainer.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.trainer.fiscal_year
        super().save(*args, **kwargs)

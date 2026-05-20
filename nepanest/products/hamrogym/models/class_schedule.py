from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.mixins.erp import ERPBaseModel


DAY_OF_WEEK_CHOICES = [
    ("monday", "Monday"),
    ("tuesday", "Tuesday"),
    ("wednesday", "Wednesday"),
    ("thursday", "Thursday"),
    ("friday", "Friday"),
    ("saturday", "Saturday"),
    ("sunday", "Sunday"),
]


CLASS_SESSION_STATUS_CHOICES = [
    ("scheduled", "Scheduled"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

CLASS_BOOKING_STATUS_CHOICES = [
    ("booked", "Booked"),
    ("cancelled", "Cancelled"),
]

CLASS_ATTENDANCE_STATUS_CHOICES = [
    ("present", "Present"),
    ("absent", "Absent"),
    ("late", "Late"),
]

CLASS_CANCELLED_BY_CHOICES = [
    ("member", "Member"),
    ("trainer", "Trainer"),
    ("admin", "Admin"),
]

class ClassSchedule(ERPBaseModel):
    gym_class = models.ForeignKey(
        "GymClass",
        on_delete=models.CASCADE,
        related_name="class_schedules",
    )
    class_room = models.ForeignKey(
        "ClassRoom",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_schedules",
    )
    trainer = models.ForeignKey(
        "Trainer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_schedules",
    )
    day_of_week = models.CharField(max_length=10, choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["day_of_week", "start_time", "gym_class__name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["gym_class", "day_of_week", "start_time", "end_time", "class_room"],
                name="unique_hamrogym_class_schedule_slot",
            ),
        ]

    def __str__(self):
        return f"{self.gym_class} - {self.get_day_of_week_display()} {self.start_time:%H:%M}"

    def clean(self):
        super().clean()
        errors = {}

        if self.end_time and self.start_time and self.end_time <= self.start_time:
            errors["end_time"] = "End time must be later than start time."

        if (
            self.trainer_id
            and self.branch_id
            and self.trainer.branch_id
            and self.trainer.branch_id != self.branch_id
        ):
            errors["trainer"] = "Trainer branch must match the class schedule branch."

        if (
            self.class_room_id
            and self.branch_id
            and self.class_room.branch_id
            and self.class_room.branch_id != self.branch_id
        ):
            errors["class_room"] = "Class room branch must match the class schedule branch."

        if (
            self.gym_class_id
            and self.branch_id
            and self.gym_class.branch_id
            and self.gym_class.branch_id != self.branch_id
        ):
            errors["gym_class"] = "Gym class branch must match the class schedule branch."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        source = self.gym_class or self.trainer or self.class_room
        if source:
            if getattr(source, "branch_id", None) and not self.branch_id:
                self.branch = source.branch
            if getattr(source, "organization_id", None) and not self.organization_id:
                self.organization = source.organization
            if getattr(source, "fiscal_year_id", None) and not self.fiscal_year_id:
                self.fiscal_year = source.fiscal_year
        super().save(*args, **kwargs)





class ClassSession(ERPBaseModel):
    class_schedule = models.ForeignKey(
        ClassSchedule,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    session_date = models.DateField()

    start_time = models.TimeField()
    end_time = models.TimeField()

    trainer = models.ForeignKey(
        "Trainer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_sessions"
    )

    status = models.CharField(
        max_length=20,
        choices=CLASS_SESSION_STATUS_CHOICES,
        default="scheduled"
    )

    max_capacity = models.PositiveIntegerField()

    class Meta:
        ordering = ["-session_date", "start_time"]
        unique_together = ("class_schedule", "session_date")

    def __str__(self):
        return f"{self.class_schedule.gym_class} - {self.session_date}"

    def clean(self):
        super().clean()
        errors = {}

        if self.end_time and self.start_time and self.end_time <= self.start_time:
            errors["end_time"] = "End time must be later than start time."

        if self.max_capacity is not None and self.max_capacity < 1:
            errors["max_capacity"] = "Max capacity must be at least 1."

        if (
            self.trainer_id
            and self.branch_id
            and self.trainer.branch_id
            and self.trainer.branch_id != self.branch_id
        ):
            errors["trainer"] = "Trainer branch must match the class session branch."

        if (
            self.class_schedule_id
            and self.branch_id
            and self.class_schedule.branch_id
            and self.class_schedule.branch_id != self.branch_id
        ):
            errors["class_schedule"] = "Class schedule branch must match the class session branch."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.class_schedule_id:
            if self.class_schedule.branch_id and not self.branch_id:
                self.branch = self.class_schedule.branch
            if self.class_schedule.organization_id and not self.organization_id:
                self.organization = self.class_schedule.organization
            if self.class_schedule.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.class_schedule.fiscal_year
            if self.class_schedule.trainer_id and not self.trainer_id:
                self.trainer = self.class_schedule.trainer
            if not self.max_capacity:
                self.max_capacity = self.class_schedule.gym_class.max_capacity
        super().save(*args, **kwargs)


class ClassBooking(ERPBaseModel):
    class_session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    member = models.ForeignKey(
        "Member",
        on_delete=models.PROTECT,
        related_name="class_bookings",
    )
    status = models.CharField(
        max_length=20,
        choices=CLASS_BOOKING_STATUS_CHOICES,
        default="booked",
    )

    class Meta:
        ordering = ["class_session__session_date", "member__member_code", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_session", "member"],
                name="unique_hamrogym_class_booking_member_session",
            ),
        ]

    def __str__(self):
        return f"{self.member} booking for {self.class_session}"

    def clean(self):
        super().clean()
        errors = {}
        if (
            self.member_id
            and self.branch_id
            and self.member.branch_id
            and self.member.branch_id != self.branch_id
        ):
            errors["member"] = "Member branch must match the class booking branch."
        if (
            self.class_session_id
            and self.branch_id
            and self.class_session.branch_id
            and self.class_session.branch_id != self.branch_id
        ):
            errors["class_session"] = "Class session branch must match the class booking branch."
        if self.class_session_id and self.status == "booked":
            booked_qs = self.class_session.bookings.filter(status="booked")
            if self.pk:
                booked_qs = booked_qs.exclude(pk=self.pk)
            if booked_qs.count() >= self.class_session.max_capacity:
                errors["member"] = "This class session is already at full capacity."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.class_session_id:
            if self.class_session.branch_id and not self.branch_id:
                self.branch = self.class_session.branch
            if self.class_session.organization_id and not self.organization_id:
                self.organization = self.class_session.organization
            if self.class_session.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.class_session.fiscal_year
        super().save(*args, **kwargs)


class ClassAttendance(ERPBaseModel):
    class_session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    member = models.ForeignKey(
        "Member",
        on_delete=models.PROTECT,
        related_name="class_attendance_records",
    )
    booking = models.ForeignKey(
        ClassBooking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_records",
    )
    status = models.CharField(
        max_length=20,
        choices=CLASS_ATTENDANCE_STATUS_CHOICES,
        default="present",
    )
    checked_in_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["class_session__session_date", "member__member_code", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_session", "member"],
                name="unique_hamrogym_class_attendance_member_session",
            ),
        ]

    def __str__(self):
        return f"{self.member} attendance for {self.class_session}"

    def clean(self):
        super().clean()
        errors = {}
        if self.booking_id:
            if self.class_session_id and self.booking.class_session_id != self.class_session_id:
                errors["booking"] = "Selected booking does not belong to this class session."
            if self.member_id and self.booking.member_id != self.member_id:
                errors["booking"] = "Selected booking does not belong to this member."
        if (
            self.member_id
            and self.branch_id
            and self.member.branch_id
            and self.member.branch_id != self.branch_id
        ):
            errors["member"] = "Member branch must match the class attendance branch."
        if (
            self.class_session_id
            and self.branch_id
            and self.class_session.branch_id
            and self.class_session.branch_id != self.branch_id
        ):
            errors["class_session"] = "Class session branch must match the class attendance branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.class_session_id:
            if self.class_session.branch_id and not self.branch_id:
                self.branch = self.class_session.branch
            if self.class_session.organization_id and not self.organization_id:
                self.organization = self.class_session.organization
            if self.class_session.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.class_session.fiscal_year
        if self.booking_id and not self.member_id:
            self.member = self.booking.member
        super().save(*args, **kwargs)


class ClassWaitlist(ERPBaseModel):
    class_session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name="waitlists",
    )
    member = models.ForeignKey(
        "Member",
        on_delete=models.PROTECT,
        related_name="class_waitlists",
    )
    waitlist_position = models.PositiveIntegerField()
    promoted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["waitlist_position", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["class_session", "member"],
                name="unique_hamrogym_class_waitlist_member_session",
            ),
            models.UniqueConstraint(
                fields=["class_session", "waitlist_position"],
                name="unique_hamrogym_class_waitlist_position_session",
            ),
        ]

    def __str__(self):
        return f"{self.member} Waitlist #{self.waitlist_position}"

    def clean(self):
        super().clean()
        errors = {}
        if self.waitlist_position < 1:
            errors["waitlist_position"] = "Waitlist position must be at least 1."
        if (
            self.member_id
            and self.branch_id
            and self.member.branch_id
            and self.member.branch_id != self.branch_id
        ):
            errors["member"] = "Member branch must match the class waitlist branch."
        if (
            self.class_session_id
            and self.branch_id
            and self.class_session.branch_id
            and self.class_session.branch_id != self.branch_id
        ):
            errors["class_session"] = "Class session branch must match the class waitlist branch."
        if self.class_session_id and self.class_session.bookings.filter(member_id=self.member_id, status="booked").exists():
            errors["member"] = "This member is already booked for the class session."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.class_session_id:
            if self.class_session.branch_id and not self.branch_id:
                self.branch = self.class_session.branch
            if self.class_session.organization_id and not self.organization_id:
                self.organization = self.class_session.organization
            if self.class_session.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.class_session.fiscal_year
        super().save(*args, **kwargs)


class ClassCancellation(ERPBaseModel):
    class_session = models.OneToOneField(
        ClassSession,
        on_delete=models.CASCADE,
        related_name="cancellation",
    )
    cancelled_by = models.CharField(
        max_length=20,
        choices=CLASS_CANCELLED_BY_CHOICES,
        default="admin",
    )
    reason = models.TextField(blank=True)
    cancellation_time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-cancellation_time", "-id"]

    def __str__(self):
        return f"Cancellation for {self.class_session}"

    def clean(self):
        super().clean()
        errors = {}
        if (
            self.class_session_id
            and self.branch_id
            and self.class_session.branch_id
            and self.class_session.branch_id != self.branch_id
        ):
            errors["class_session"] = "Class session branch must match the cancellation branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.class_session_id:
            if self.class_session.branch_id and not self.branch_id:
                self.branch = self.class_session.branch
            if self.class_session.organization_id and not self.organization_id:
                self.organization = self.class_session.organization
            if self.class_session.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.class_session.fiscal_year
        super().save(*args, **kwargs)
        if self.class_session_id and self.class_session.status != "cancelled":
            self.class_session.status = "cancelled"
            self.class_session.save(update_fields=["status", "updated_at"])

from django.core.exceptions import ValidationError
from django.db import models
from core.mixins.erp import ERPBaseModel
from .exercise import DIFFICULTY_LEVEL_CHOICES


class WorkoutPlan(ERPBaseModel):
    name = models.CharField(max_length=200, unique=True)
    fitness_goal = models.ForeignKey("FitnessGoal", on_delete=models.CASCADE, null=True, blank=True, related_name="workout_plans")
    difficulty_level = models.CharField(max_length=20, null=True, blank=True, choices=DIFFICULTY_LEVEL_CHOICES)
    duration_week = models.PositiveIntegerField(null=True, blank=True)
    days_per_week = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class WorkoutWeek(ERPBaseModel):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="workout_weeks")
    week_number = models.PositiveIntegerField()

    class Meta:
        ordering = ["week_number", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["workout_plan", "week_number"],
                name="unique_hamrogym_workout_week_number_per_plan",
            ),
        ]

    def __str__(self) -> str:
        return f"Week {self.week_number} of {self.workout_plan.name}"


class WorkoutDay(ERPBaseModel):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="days")
    workout_week = models.ForeignKey(
        WorkoutWeek,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="days",
    )
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=100)

    class Meta:
        ordering = ["day_number", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["workout_plan", "day_number"],
                name="unique_hamrogym_workout_day_number_per_plan",
            ),
        ]

    def __str__(self) -> str:
        return f"Day {self.day_number} - {self.title} ({self.workout_plan.name})"

    def clean(self):
        super().clean()
        errors = {}
        if self.workout_week_id and self.workout_plan_id and self.workout_week.workout_plan_id != self.workout_plan_id:
            errors["workout_week"] = "Selected week must belong to the same workout plan."
        if not self.title:
            errors["title"] = "Day title is required."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.workout_week_id and not self.workout_plan_id:
            self.workout_plan = self.workout_week.workout_plan
        if not self.title:
            self.title = f"Day {self.day_number}"
        super().save(*args, **kwargs)


class WorkoutExercise(ERPBaseModel):
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name="exercises")
    exercise = models.ForeignKey("Exercise", on_delete=models.CASCADE, related_name="planned_workouts")
    sets = models.PositiveIntegerField(null=True, blank=True)
    reps = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    rest_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    sequence_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sequence_order", "id"]

    def __str__(self) -> str:
        return f"{self.exercise.name} on {self.workout_day}"


class WorkoutAssignment(ERPBaseModel):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('stopped', 'Stopped'),
    ]

    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="workout_assignments")
    trainer = models.ForeignKey("Trainer", on_delete=models.SET_NULL, null=True, blank=True, related_name="workout_assignments")

    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.PROTECT, related_name="assignments")

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.member} - {self.workout_plan}"

    def clean(self):
        super().clean()
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be earlier than start date."})
    
    
class WorkoutLog(ERPBaseModel):

    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="workout_logs")
    workout_assignment = models.ForeignKey(WorkoutAssignment, on_delete=models.CASCADE, related_name="logs")

    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs")
    exercise = models.ForeignKey("Exercise", on_delete=models.SET_NULL, null=True, blank=True, related_name="workout_logs")

    date = models.DateField()

    sets_completed = models.IntegerField(null=True, blank=True)
    reps_completed = models.IntegerField(null=True, blank=True)

    weight_used = models.FloatField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-date", "-id"]

    def clean(self):
        super().clean()
        errors = {}
        if self.workout_assignment_id and self.member_id and self.workout_assignment.member_id != self.member_id:
            errors["member"] = "Selected member must match the workout assignment member."
        if self.workout_day_id and self.workout_assignment_id:
            assignment_plan_id = self.workout_assignment.workout_plan_id
            if self.workout_day.workout_plan_id != assignment_plan_id:
                errors["workout_day"] = "Selected workout day must belong to the assignment's workout plan."
        if self.exercise_id and self.workout_day_id:
            if not self.workout_day.exercises.filter(exercise_id=self.exercise_id).exists():
                errors["exercise"] = "Selected exercise is not part of the chosen workout day."
        if errors:
            raise ValidationError(errors)


class PersonalBest(ERPBaseModel):
    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="personal_bests")
    exercise = models.ForeignKey("Exercise", on_delete=models.CASCADE, related_name="personal_bests")
    best_weight = models.FloatField(null=True, blank=True)
    best_reps = models.IntegerField(null=True, blank=True)
    best_duration = models.IntegerField(null=True, blank=True)
    achieved_on = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member", "exercise"],
                name="unique_hamrogym_personal_best_member_exercise",
            ),
        ]
        ordering = ["member_id", "exercise_id"]

    def __str__(self):
        return f"{self.member} - {self.exercise}"

    def clean(self):
        super().clean()
        if self.best_weight is None and self.best_reps is None and self.best_duration is None:
            raise ValidationError("At least one personal best metric is required.")


class WorkoutPlanVersion(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="versions")
    version_number = models.IntegerField()
    change_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["workout_plan", "version_number"],
                name="unique_hamrogym_plan_version_number",
            ),
        ]
        ordering = ["-version_number", "-id"]

    def __str__(self):
        return f"{self.workout_plan.name} v{self.version_number}"

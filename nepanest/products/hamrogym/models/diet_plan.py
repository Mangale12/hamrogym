from django.core.exceptions import ValidationError
from django.db import models

from core.mixins.erp import ERPBaseModel


class DietPlan(ERPBaseModel):
    class GoalType(models.TextChoices):
        FAT_LOSS = "fat_loss", "Fat Loss"
        MUSCLE_GAIN = "muscle_gain", "Muscle Gain"
        MAINTENANCE = "maintenance", "Maintenance"
        MEDICAL = "medical", "Medical"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=200, unique=True)
    goal_type = models.CharField(max_length=20, choices=GoalType.choices)
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    trainer = models.ForeignKey(
        "Trainer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diet_plans",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        errors = {}
        if self.duration_days is not None and self.duration_days < 1:
            errors["duration_days"] = "Duration days must be at least 1."
        if (
            self.trainer_id
            and self.branch_id
            and self.trainer.branch_id
            and self.trainer.branch_id != self.branch_id
        ):
            errors["trainer"] = "Trainer branch must match the diet plan branch."
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
        self.is_active = self.status == self.Status.ACTIVE
        super().save(*args, **kwargs)


class DietDay(ERPBaseModel):
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["day_number", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["diet_plan", "day_number"],
                name="unique_hamrogym_diet_day_number_per_plan",
            ),
        ]

    def __str__(self):
        return f"{self.diet_plan.name} - Day {self.day_number}"

    def clean(self):
        super().clean()
        if self.diet_plan_id and self.branch_id and self.diet_plan.branch_id and self.diet_plan.branch_id != self.branch_id:
            raise ValidationError({"diet_plan": "Diet plan branch must match the diet day branch."})

    def save(self, *args, **kwargs):
        if self.diet_plan_id:
            if self.diet_plan.branch_id and not self.branch_id:
                self.branch = self.diet_plan.branch
            if self.diet_plan.organization_id and not self.organization_id:
                self.organization = self.diet_plan.organization
            if self.diet_plan.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.diet_plan.fiscal_year
        if not self.title:
            self.title = f"Day {self.day_number}"
        super().save(*args, **kwargs)


class Meal(ERPBaseModel):
    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        DINNER = "dinner", "Dinner"
        SNACK = "snack", "Snack"
        PRE_WORKOUT = "pre_workout", "Pre Workout"
        POST_WORKOUT = "post_workout", "Post Workout"

    diet_day = models.ForeignKey(DietDay, on_delete=models.CASCADE, related_name="meals")
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    food_items = models.TextField()
    instructions = models.TextField(blank=True)
    calories = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    protein_grams = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    carbs_grams = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fat_grams = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    sequence_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["sequence_order", "id"]

    def __str__(self):
        return f"{self.get_meal_type_display()} - {self.diet_day}"

    def clean(self):
        super().clean()
        errors = {}
        for field_name in ("calories", "protein_grams", "carbs_grams", "fat_grams"):
            value = getattr(self, field_name)
            if value is not None and value < 0:
                errors[field_name] = "Nutrition values cannot be negative."
        if self.diet_day_id and self.branch_id and self.diet_day.branch_id and self.diet_day.branch_id != self.branch_id:
            errors["diet_day"] = "Diet day branch must match the meal branch."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.diet_day_id:
            if self.diet_day.branch_id and not self.branch_id:
                self.branch = self.diet_day.branch
            if self.diet_day.organization_id and not self.organization_id:
                self.organization = self.diet_day.organization
            if self.diet_day.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.diet_day.fiscal_year
        super().save(*args, **kwargs)


class DietAssignment(ERPBaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        STOPPED = "stopped", "Stopped"

    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="diet_assignments")
    trainer = models.ForeignKey("Trainer", on_delete=models.SET_NULL, null=True, blank=True, related_name="diet_assignments")
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.PROTECT, related_name="assignments")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return f"{self.member} - {self.diet_plan}"

    def clean(self):
        super().clean()
        errors = {}
        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["end_date"] = "End date cannot be earlier than start date."
        if self.member_id and self.branch_id and self.member.branch_id and self.member.branch_id != self.branch_id:
            errors["member"] = "Member branch must match the assignment branch."
        if self.trainer_id and self.branch_id and self.trainer.branch_id and self.trainer.branch_id != self.branch_id:
            errors["trainer"] = "Trainer branch must match the assignment branch."
        if self.diet_plan_id and self.branch_id and self.diet_plan.branch_id and self.diet_plan.branch_id != self.branch_id:
            errors["diet_plan"] = "Diet plan branch must match the assignment branch."
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


class DietLog(ERPBaseModel):
    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="diet_logs")
    diet_assignment = models.ForeignKey(DietAssignment, on_delete=models.CASCADE, related_name="logs")
    diet_day = models.ForeignKey(DietDay, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs")
    meal = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs")
    date = models.DateField()
    followed = models.BooleanField(default=True)
    deviation_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "diet_assignment", "diet_day", "meal", "date"],
                name="unique_hamrogym_diet_log_entry",
            ),
        ]

    def __str__(self):
        meal_label = self.meal.get_meal_type_display() if self.meal_id else "Meal"
        return f"{self.member} - {self.date} - {meal_label}"

    def clean(self):
        super().clean()
        errors = {}
        if self.diet_assignment_id and self.member_id and self.diet_assignment.member_id != self.member_id:
            errors["member"] = "Selected member must match the diet assignment member."
        if self.diet_day_id and self.diet_assignment_id:
            if self.diet_day.diet_plan_id != self.diet_assignment.diet_plan_id:
                errors["diet_day"] = "Selected diet day must belong to the assignment's diet plan."
        if self.meal_id and self.diet_day_id and self.meal.diet_day_id != self.diet_day_id:
            errors["meal"] = "Selected meal must belong to the chosen diet day."
        if self.meal_id and self.diet_assignment_id:
            assignment_plan_id = self.diet_assignment.diet_plan_id
            if self.meal.diet_day.diet_plan_id != assignment_plan_id:
                errors["meal"] = "Selected meal must belong to the assignment's diet plan."
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


class NutritionGoal(ERPBaseModel):
    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="nutrition_goals")
    daily_calories_target = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    protein_target = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    carbs_target = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fat_target = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-start_date", "-id"]

    def __str__(self):
        return f"{self.member} Nutrition Goal"

    def clean(self):
        super().clean()
        errors = {}
        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["end_date"] = "End date cannot be earlier than start date."
        for field_name in ("daily_calories_target", "protein_target", "carbs_target", "fat_target"):
            value = getattr(self, field_name)
            if value is not None and value < 0:
                errors[field_name] = "Target values cannot be negative."
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


class WaterIntakeLog(ERPBaseModel):
    member = models.ForeignKey("Member", on_delete=models.CASCADE, related_name="water_logs")
    date = models.DateField()
    quantity_liters = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["-date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "date"],
                name="unique_hamrogym_water_intake_per_member_day",
            ),
        ]

    def __str__(self):
        return f"{self.member} - {self.quantity_liters}L on {self.date}"

    def clean(self):
        super().clean()
        if self.quantity_liters <= 0:
            raise ValidationError({"quantity_liters": "Water intake must be greater than zero."})

    def save(self, *args, **kwargs):
        if self.member_id:
            if self.member.branch_id and not self.branch_id:
                self.branch = self.member.branch
            if self.member.organization_id and not self.organization_id:
                self.organization = self.member.organization
            if self.member.fiscal_year_id and not self.fiscal_year_id:
                self.fiscal_year = self.member.fiscal_year
        super().save(*args, **kwargs)

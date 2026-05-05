from django.db import models
from core.mixins.erp import ERPBaseModel


# =========================
# CONSTANTS / CHOICES
# =========================


MEAL_TYPE_CHOICES = [
    ("breakfast", "Breakfast"),
    ("lunch", "Lunch"),
    ("dinner", "Dinner"),
    ("snack", "Snack"),
    ("pre_workout", "Pre Workout"),
    ("post_workout", "Post Workout"),
]

ASSIGNMENT_STATUS_CHOICES = [
    ("active", "Active"),
    ("completed", "Completed"),
    ("stopped", "Stopped"),
]


# =========================
# DIET PLAN (TEMPLATE)
# =========================

class DietPlan(ERPBaseModel):
    name = models.CharField(max_length=200)
    fitness_goal = models.ForeignKey("FitnessGoal", on_delete=models.CASCADE, null=True, blank=True, related_name="diet_plans")

    duration_days = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    trainer = models.ForeignKey(
        "Trainer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diet_plans"
    )

    status = models.BooleanField(default=True)  # active/inactive

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name


# =========================
# DIET DAY
# =========================

# class DietDay(ERPBaseModel):
#     diet_plan = models.ForeignKey(
#         DietPlan,
#         on_delete=models.CASCADE,
#         related_name="days"
#     )

#     day_number = models.PositiveIntegerField()
#     title = models.CharField(max_length=200, blank=True, null=True)

#     class Meta:
#         unique_together = ("diet_plan", "day_number")
#         ordering = ["day_number"]

#     def __str__(self):
#         return f"{self.diet_plan.name} - Day {self.day_number}"


# # =========================
# # MEAL
# # =========================

# class Meal(ERPBaseModel):
#     diet_day = models.ForeignKey(
#         DietDay,
#         on_delete=models.CASCADE,
#         related_name="meals"
#     )

#     meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)

#     food_items = models.TextField(help_text="Comma separated or description")
#     instructions = models.TextField(blank=True, null=True)

#     # Nutrition (optional)
#     calories = models.FloatField(null=True, blank=True)
#     protein_grams = models.FloatField(null=True, blank=True)
#     carbs_grams = models.FloatField(null=True, blank=True)
#     fat_grams = models.FloatField(null=True, blank=True)

#     sequence_order = models.PositiveIntegerField(default=1)

#     class Meta:
#         ordering = ["sequence_order"]

#     def __str__(self):
#         return f"{self.meal_type} - {self.diet_day}"


# # =========================
# # DIET ASSIGNMENT
# # =========================

# class DietAssignment(ERPBaseModel):
#     member = models.ForeignKey(
#         "Member",
#         on_delete=models.CASCADE,
#         related_name="diet_assignments"
#     )

#     trainer = models.ForeignKey(
#         "Trainer",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="assigned_diets"
#     )

#     diet_plan = models.ForeignKey(
#         DietPlan,
#         on_delete=models.CASCADE,
#         related_name="assignments"
#     )

#     start_date = models.DateField()
#     end_date = models.DateField()

#     status = models.CharField(
#         max_length=20,
#         choices=ASSIGNMENT_STATUS_CHOICES,
#         default="active"
#     )

#     class Meta:
#         ordering = ["-start_date"]

#     def __str__(self):
#         return f"{self.member} - {self.diet_plan}"


# # =========================
# # DIET LOG (TRACKING)
# # =========================

# class DietLog(ERPBaseModel):
#     member = models.ForeignKey(
#         "Member",
#         on_delete=models.CASCADE,
#         related_name="diet_logs"
#     )

#     diet_assignment = models.ForeignKey(
#         DietAssignment,
#         on_delete=models.CASCADE,
#         related_name="logs"
#     )

#     diet_day = models.ForeignKey(
#         DietDay,
#         on_delete=models.CASCADE
#     )

#     meal = models.ForeignKey(
#         Meal,
#         on_delete=models.CASCADE
#     )

#     date = models.DateField()

#     followed = models.BooleanField(default=True)
#     deviation_notes = models.TextField(blank=True, null=True)

#     class Meta:
#         unique_together = ("member", "meal", "date")

#     def __str__(self):
#         return f"{self.member} - {self.date} - {self.meal}"


# # =========================
# # NUTRITION GOAL
# # =========================

# class NutritionGoal(ERPBaseModel):
#     member = models.ForeignKey(
#         "Member",
#         on_delete=models.CASCADE,
#         related_name="nutrition_goals"
#     )

#     daily_calories_target = models.FloatField(null=True, blank=True)
#     protein_target = models.FloatField(null=True, blank=True)
#     carbs_target = models.FloatField(null=True, blank=True)
#     fat_target = models.FloatField(null=True, blank=True)

#     start_date = models.DateField()
#     end_date = models.DateField(null=True, blank=True)

#     class Meta:
#         ordering = ["-start_date"]

#     def __str__(self):
#         return f"{self.member} Nutrition Goal"


# # =========================
# # WATER INTAKE LOG (OPTIONAL)
# # =========================

# class WaterIntakeLog(ERPBaseModel):
    member = models.ForeignKey(
        "Member",
        on_delete=models.CASCADE,
        related_name="water_logs"
    )

    date = models.DateField()
    quantity_liters = models.FloatField()

    class Meta:
        unique_together = ("member", "date")

    def __str__(self):
        return f"{self.member} - {self.quantity_liters}L on {self.date}"
from core.datatables.views import BaseDataTableView

from ..models import DietAssignment, DietDay, DietLog, DietPlan, Meal, NutritionGoal, WaterIntakeLog


DIET_PLAN_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("goal_type", lambda obj: obj.get_goal_type_display()),
    ("duration_days", lambda obj: obj.duration_days or "-"),
    ("trainer", lambda obj: str(obj.trainer) if obj.trainer else "-"),
    ("status", lambda obj: obj.get_status_display()),
]

DIET_DAY_COLUMNS = [
    ("id", "id"),
    ("diet_plan", lambda obj: obj.diet_plan.name),
    ("day_number", "day_number"),
    ("title", lambda obj: obj.title or "-"),
]

MEAL_COLUMNS = [
    ("id", "id"),
    ("diet_day", lambda obj: str(obj.diet_day)),
    ("meal_type", lambda obj: obj.get_meal_type_display()),
    ("food_items", "food_items"),
    ("calories", lambda obj: obj.calories or "-"),
    ("sequence_order", "sequence_order"),
]

DIET_ASSIGNMENT_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: str(obj.member)),
    ("trainer", lambda obj: str(obj.trainer) if obj.trainer else "-"),
    ("diet_plan", lambda obj: obj.diet_plan.name),
    ("start_date", "start_date"),
    ("end_date", lambda obj: obj.end_date or "-"),
    ("status", lambda obj: obj.get_status_display()),
]

DIET_LOG_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: str(obj.member)),
    ("diet_assignment", lambda obj: str(obj.diet_assignment)),
    ("diet_day", lambda obj: str(obj.diet_day) if obj.diet_day else "-"),
    ("meal", lambda obj: obj.meal.get_meal_type_display() if obj.meal else "-"),
    ("date", "date"),
    ("followed", lambda obj: "Yes" if obj.followed else "No"),
]

NUTRITION_GOAL_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: str(obj.member)),
    ("daily_calories_target", lambda obj: obj.daily_calories_target or "-"),
    ("protein_target", lambda obj: obj.protein_target or "-"),
    ("carbs_target", lambda obj: obj.carbs_target or "-"),
    ("fat_target", lambda obj: obj.fat_target or "-"),
    ("start_date", "start_date"),
    ("end_date", lambda obj: obj.end_date or "-"),
]

WATER_INTAKE_LOG_COLUMNS = [
    ("id", "id"),
    ("member", lambda obj: str(obj.member)),
    ("date", "date"),
    ("quantity_liters", "quantity_liters"),
]


class DietPlanDataTableView(BaseDataTableView):
    model = DietPlan
    columns = DIET_PLAN_COLUMNS
    searchable_columns = ["name", "goal_type", "trainer__employee__employee_id", "trainer__employee__user__first_name", "status"]
    orderable_columns = ["id", "name", "goal_type", "duration_days", "trainer__employee__employee_id", "status"]


class DietDayDataTableView(BaseDataTableView):
    model = DietDay
    columns = DIET_DAY_COLUMNS
    searchable_columns = ["diet_plan__name", "title"]
    orderable_columns = ["id", "diet_plan__name", "day_number", "title"]


class MealDataTableView(BaseDataTableView):
    model = Meal
    columns = MEAL_COLUMNS
    searchable_columns = ["diet_day__diet_plan__name", "meal_type", "food_items", "instructions"]
    orderable_columns = ["id", "diet_day__diet_plan__name", "meal_type", "calories", "sequence_order"]


class DietAssignmentDataTableView(BaseDataTableView):
    model = DietAssignment
    columns = DIET_ASSIGNMENT_COLUMNS
    searchable_columns = ["member__member_code", "member__party__name", "diet_plan__name", "trainer__employee__employee_id", "status"]
    orderable_columns = ["id", "member__member_code", "diet_plan__name", "start_date", "end_date", "status"]


class DietLogDataTableView(BaseDataTableView):
    model = DietLog
    columns = DIET_LOG_COLUMNS
    searchable_columns = ["member__member_code", "member__party__name", "diet_assignment__diet_plan__name", "meal__meal_type", "deviation_notes"]
    orderable_columns = ["id", "member__member_code", "date", "followed"]


class NutritionGoalDataTableView(BaseDataTableView):
    model = NutritionGoal
    columns = NUTRITION_GOAL_COLUMNS
    searchable_columns = ["member__member_code", "member__party__name"]
    orderable_columns = ["id", "member__member_code", "daily_calories_target", "start_date", "end_date"]


class WaterIntakeLogDataTableView(BaseDataTableView):
    model = WaterIntakeLog
    columns = WATER_INTAKE_LOG_COLUMNS
    searchable_columns = ["member__member_code", "member__party__name"]
    orderable_columns = ["id", "member__member_code", "date", "quantity_liters"]

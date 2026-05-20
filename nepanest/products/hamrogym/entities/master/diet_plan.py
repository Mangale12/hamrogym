from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.diet_data_table import (
    DIET_ASSIGNMENT_COLUMNS,
    DIET_DAY_COLUMNS,
    DIET_LOG_COLUMNS,
    DIET_PLAN_COLUMNS,
    MEAL_COLUMNS,
    NUTRITION_GOAL_COLUMNS,
    WATER_INTAKE_LOG_COLUMNS,
    DietAssignmentDataTableView,
    DietDayDataTableView,
    DietLogDataTableView,
    DietPlanDataTableView,
    MealDataTableView,
    NutritionGoalDataTableView,
    WaterIntakeLogDataTableView,
)
from ...forms.diet_plan_form import (
    DietAssignmentForm,
    DietDayForm,
    DietLogForm,
    DietPlanForm,
    MealForm,
    NutritionGoalForm,
    WaterIntakeLogForm,
)
from ...models import DietAssignment, DietDay, DietLog, DietPlan, Meal, NutritionGoal, WaterIntakeLog


def _title(key):
    return key.replace("_", " ").title()


register_entity(
    EntityConfig(
        name="diet_plan",
        url_path="diet-plans",
        verbose_name="Diet Plan",
        model=DietPlan,
        form_class=DietPlanForm,
        datatable_view=DietPlanDataTableView,
        fields=[
            {"name": "name", "label": "Name", "type": "text", "required": True, "col": 4},
            {
                "name": "goal_type",
                "label": "Goal Type",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": [("", "Select Goal Type"), *DietPlan.GoalType.choices],
            },
            {"name": "duration_days", "label": "Duration (Days)", "type": "number", "required": False, "col": 4},
            {"name": "trainer", "label": "Created By", "type": "select", "required": False, "col": 6, "url_name": "trainer_select"},
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": [("", "Select Status"), *DietPlan.Status.choices],
            },
            {"name": "description", "label": "Description", "type": "textarea", "required": False, "col": 12},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key)}
            for key, _accessor in DIET_PLAN_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": DietPlan.Status.ACTIVE},
        select_search_fields=["name", "goal_type"],
        select_label_func=lambda obj: f"{obj.name} ({obj.get_goal_type_display()})",
    )
)

register_entity(
    EntityConfig(
        name="diet_day",
        url_path="diet-days",
        verbose_name="Diet Day",
        model=DietDay,
        form_class=DietDayForm,
        datatable_view=DietDayDataTableView,
        fields=[
            {"name": "diet_plan", "label": "Diet Plan", "type": "select", "required": True, "col": 6, "url_name": "diet_plan_select"},
            {"name": "day_number", "label": "Day Number", "type": "number", "required": True, "col": 3},
            {"name": "title", "label": "Title", "type": "text", "required": False, "col": 3},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key)}
            for key, _accessor in DIET_DAY_COLUMNS
            if key != "id"
        ],
        select_search_fields=["diet_plan__name", "title"],
        select_label_func=lambda obj: f"{obj.diet_plan.name} - Day {obj.day_number}",
    )
)

register_entity(
    EntityConfig(
        name="meal",
        url_path="meals",
        verbose_name="Meal",
        model=Meal,
        form_class=MealForm,
        datatable_view=MealDataTableView,
        fields=[
            {"name": "diet_day", "label": "Diet Day", "type": "select", "required": True, "col": 4, "url_name": "diet_day_select"},
            {
                "name": "meal_type",
                "label": "Meal Type",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": [("", "Select Meal Type"), *Meal.MealType.choices],
            },
            {"name": "sequence_order", "label": "Sequence Order", "type": "number", "required": True, "col": 4},
            {"name": "food_items", "label": "Food Items", "type": "textarea", "required": True, "col": 12},
            {"name": "instructions", "label": "Instructions", "type": "textarea", "required": False, "col": 12},
            {"name": "calories", "label": "Calories", "type": "number", "required": False, "col": 3},
            {"name": "protein_grams", "label": "Protein (g)", "type": "number", "required": False, "col": 3},
            {"name": "carbs_grams", "label": "Carbs (g)", "type": "number", "required": False, "col": 3},
            {"name": "fat_grams", "label": "Fat (g)", "type": "number", "required": False, "col": 3},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key)}
            for key, _accessor in MEAL_COLUMNS
            if key != "id"
        ],
        reset_defaults={"sequence_order": 1},
        select_search_fields=["diet_day__diet_plan__name", "meal_type", "food_items"],
        select_label_func=lambda obj: f"{obj.get_meal_type_display()} - {obj.diet_day}",
    )
)

register_entity(
    EntityConfig(
        name="diet_assignment",
        url_path="diet-assignments",
        verbose_name="Diet Assignment",
        model=DietAssignment,
        form_class=DietAssignmentForm,
        datatable_view=DietAssignmentDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "trainer", "label": "Trainer", "type": "select", "required": False, "col": 4, "url_name": "trainer_select"},
            {"name": "diet_plan", "label": "Diet Plan", "type": "select", "required": True, "col": 4, "url_name": "diet_plan_select"},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": True, "col": 4},
            {"name": "end_date", "label": "End Date", "type": "date", "required": False, "col": 4},
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 4,
                "options": [("", "Select Status"), *DietAssignment.Status.choices],
            },
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key)}
            for key, _accessor in DIET_ASSIGNMENT_COLUMNS
            if key != "id"
        ],
        reset_defaults={"status": DietAssignment.Status.ACTIVE},
        select_search_fields=["member__member_code", "member__party__name", "diet_plan__name"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.diet_plan.name}",
    )
)

register_entity(
    EntityConfig(
        name="diet_log",
        url_path="diet-logs",
        verbose_name="Diet Log",
        model=DietLog,
        form_class=DietLogForm,
        datatable_view=DietLogDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "diet_assignment", "label": "Diet Assignment", "type": "select", "required": True, "col": 4, "url_name": "diet_assignment_select"},
            {"name": "date", "label": "Date", "type": "date", "required": True, "col": 4},
            {"name": "diet_day", "label": "Diet Day", "type": "select", "required": False, "col": 6, "url_name": "diet_day_select"},
            {"name": "meal", "label": "Meal", "type": "select", "required": False, "col": 6, "url_name": "meal_select"},
            {"name": "followed", "label": "Followed", "type": "checkbox", "required": False, "col": 3},
            {"name": "deviation_notes", "label": "Deviation Notes", "type": "textarea", "required": False, "col": 9},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key)}
            for key, _accessor in DIET_LOG_COLUMNS
            if key != "id"
        ],
        reset_defaults={"followed": True},
        select_search_fields=["member__member_code", "member__party__name", "diet_assignment__diet_plan__name"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.date}",
    )
)

register_entity(
    EntityConfig(
        name="nutrition_goal",
        url_path="nutrition-goals",
        verbose_name="Nutrition Goal",
        model=NutritionGoal,
        form_class=NutritionGoalForm,
        datatable_view=NutritionGoalDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "daily_calories_target", "label": "Daily Calories Target", "type": "number", "required": False, "col": 2},
            {"name": "protein_target", "label": "Protein Target", "type": "number", "required": False, "col": 2},
            {"name": "carbs_target", "label": "Carbs Target", "type": "number", "required": False, "col": 2},
            {"name": "fat_target", "label": "Fat Target", "type": "number", "required": False, "col": 2},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": True, "col": 6},
            {"name": "end_date", "label": "End Date", "type": "date", "required": False, "col": 6},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key)}
            for key, _accessor in NUTRITION_GOAL_COLUMNS
            if key != "id"
        ],
        select_search_fields=["member__member_code", "member__party__name"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.start_date}",
    )
)

register_entity(
    EntityConfig(
        name="water_intake_log",
        url_path="water-intake-logs",
        verbose_name="Water Intake Log",
        model=WaterIntakeLog,
        form_class=WaterIntakeLogForm,
        datatable_view=WaterIntakeLogDataTableView,
        fields=[
            {"name": "member", "label": "Member", "type": "select", "required": True, "col": 4, "url_name": "member_select"},
            {"name": "date", "label": "Date", "type": "date", "required": True, "col": 4},
            {"name": "quantity_liters", "label": "Quantity (Liters)", "type": "number", "required": True, "col": 4},
            {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
        ],
        datatable_columns=[
            {"name": key, "title": _title(key)}
            for key, _accessor in WATER_INTAKE_LOG_COLUMNS
            if key != "id"
        ],
        select_search_fields=["member__member_code", "member__party__name"],
        select_label_func=lambda obj: f"{obj.member.member_code} - {obj.date}",
    )
)

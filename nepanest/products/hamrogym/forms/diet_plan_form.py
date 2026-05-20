from django import forms

from .workout_plan_form import _apply_bootstrap_widgets
from ..models import DietAssignment, DietDay, DietLog, DietPlan, Meal, NutritionGoal, WaterIntakeLog


class DietPlanForm(forms.ModelForm):
    class Meta:
        model = DietPlan
        fields = [
            "name",
            "goal_type",
            "duration_days",
            "description",
            "trainer",
            "status",
            "remarks",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Example: Lean Muscle Meal Plan"}),
            "duration_days": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["duration_days"].required = False
        self.fields["description"].required = False
        self.fields["trainer"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class DietDayForm(forms.ModelForm):
    class Meta:
        model = DietDay
        fields = ["diet_plan", "day_number", "title", "remarks"]
        widgets = {
            "day_number": forms.NumberInput(attrs={"min": 1}),
            "title": forms.TextInput(attrs={"placeholder": "Example: High Protein Day"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = [
            "diet_day",
            "meal_type",
            "food_items",
            "instructions",
            "calories",
            "protein_grams",
            "carbs_grams",
            "fat_grams",
            "sequence_order",
            "remarks",
        ]
        widgets = {
            "food_items": forms.Textarea(attrs={"rows": 4, "placeholder": "Rice, grilled chicken, sauteed vegetables"}),
            "instructions": forms.Textarea(attrs={"rows": 3, "placeholder": "Steam vegetables and serve warm."}),
            "calories": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "protein_grams": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "carbs_grams": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "fat_grams": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "sequence_order": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["instructions"].required = False
        self.fields["calories"].required = False
        self.fields["protein_grams"].required = False
        self.fields["carbs_grams"].required = False
        self.fields["fat_grams"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class DietAssignmentForm(forms.ModelForm):
    class Meta:
        model = DietAssignment
        fields = [
            "member",
            "trainer",
            "diet_plan",
            "start_date",
            "end_date",
            "status",
            "remarks",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trainer"].required = False
        self.fields["end_date"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class DietLogForm(forms.ModelForm):
    class Meta:
        model = DietLog
        fields = [
            "member",
            "diet_assignment",
            "diet_day",
            "meal",
            "date",
            "followed",
            "deviation_notes",
            "remarks",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["diet_day"].required = False
        self.fields["meal"].required = False
        self.fields["deviation_notes"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class NutritionGoalForm(forms.ModelForm):
    class Meta:
        model = NutritionGoal
        fields = [
            "member",
            "daily_calories_target",
            "protein_target",
            "carbs_target",
            "fat_target",
            "start_date",
            "end_date",
            "remarks",
        ]
        widgets = {
            "daily_calories_target": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "protein_target": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "carbs_target": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "fat_target": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["daily_calories_target"].required = False
        self.fields["protein_target"].required = False
        self.fields["carbs_target"].required = False
        self.fields["fat_target"].required = False
        self.fields["end_date"].required = False
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)


class WaterIntakeLogForm(forms.ModelForm):
    class Meta:
        model = WaterIntakeLog
        fields = ["member", "date", "quantity_liters", "remarks"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "quantity_liters": forms.NumberInput(attrs={"min": 0.01, "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["remarks"].required = False
        _apply_bootstrap_widgets(self)

from django import forms

from .workout_plan_form import _apply_bootstrap_widgets
from ..models import WorkoutDay, WorkoutExercise, WorkoutWeek


class WorkoutWeekForm(forms.ModelForm):
    class Meta:
        model = WorkoutWeek
        fields = ["week_number"]
        widgets = {
            "week_number": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, workout_plan=None, **kwargs):
        self.workout_plan = workout_plan
        super().__init__(*args, **kwargs)
        _apply_bootstrap_widgets(self)

    def clean_week_number(self):
        week_number = self.cleaned_data["week_number"]
        if self.workout_plan and self.workout_plan.workout_weeks.filter(week_number=week_number).exists():
            raise forms.ValidationError("This week number already exists in the plan.")
        return week_number


class WorkoutDayForm(forms.ModelForm):
    class Meta:
        model = WorkoutDay
        fields = ["day_number", "title"]
        widgets = {
            "day_number": forms.NumberInput(attrs={"min": 1}),
            "title": forms.TextInput(attrs={"placeholder": "Example: Upper Body Strength"}),
        }

    def __init__(self, *args, workout_week=None, workout_plan=None, **kwargs):
        self.workout_week = workout_week
        self.workout_plan = workout_plan or (workout_week.workout_plan if workout_week else None)
        super().__init__(*args, **kwargs)
        _apply_bootstrap_widgets(self)

    def clean_day_number(self):
        day_number = self.cleaned_data["day_number"]
        if self.workout_plan and self.workout_plan.days.exclude(pk=self.instance.pk).filter(day_number=day_number).exists():
            raise forms.ValidationError("This day number already exists in the workout plan.")
        return day_number

    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if not title:
            raise forms.ValidationError("Day title is required.")
        return title


class WorkoutExerciseForm(forms.ModelForm):
    class Meta:
        model = WorkoutExercise
        fields = [
            "exercise",
            "sets",
            "reps",
            "weight",
            "duration_seconds",
            "rest_time_seconds",
            "sequence_order",
        ]
        widgets = {
            "sets": forms.NumberInput(attrs={"min": 0}),
            "reps": forms.NumberInput(attrs={"min": 0}),
            "weight": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "duration_seconds": forms.NumberInput(attrs={"min": 0}),
            "rest_time_seconds": forms.NumberInput(attrs={"min": 0}),
            "sequence_order": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sets"].required = False
        self.fields["reps"].required = False
        self.fields["weight"].required = False
        self.fields["duration_seconds"].required = False
        self.fields["rest_time_seconds"].required = False
        _apply_bootstrap_widgets(self)

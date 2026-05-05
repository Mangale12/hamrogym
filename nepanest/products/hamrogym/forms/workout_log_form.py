from django import forms

from .workout_plan_form import _apply_bootstrap_widgets
from ..models import WorkoutLog


class WorkoutLogForm(forms.ModelForm):
    class Meta:
        model = WorkoutLog
        fields = [
            "member",
            "workout_assignment",
            "workout_day",
            "exercise",
            "date",
            "sets_completed",
            "reps_completed",
            "weight_used",
            "duration_seconds",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "sets_completed": forms.NumberInput(attrs={"min": 0}),
            "reps_completed": forms.NumberInput(attrs={"min": 0}),
            "weight_used": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "duration_seconds": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["workout_day"].required = False
        self.fields["exercise"].required = False
        self.fields["sets_completed"].required = False
        self.fields["reps_completed"].required = False
        self.fields["weight_used"].required = False
        self.fields["duration_seconds"].required = False
        self.fields["notes"].required = False
        self.fields["member"].queryset = self.fields["member"].queryset.order_by("member_code", "id")
        self.fields["workout_assignment"].queryset = self.fields["workout_assignment"].queryset.select_related(
            "member",
            "workout_plan",
        ).order_by("-start_date", "-id")
        self.fields["workout_day"].queryset = self.fields["workout_day"].queryset.select_related(
            "workout_plan",
            "workout_week",
        ).order_by("day_number", "id")
        self.fields["exercise"].queryset = self.fields["exercise"].queryset.order_by("name", "id")
        _apply_bootstrap_widgets(self)

    def clean(self):
        cleaned_data = super().clean()
        member = cleaned_data.get("member")
        assignment = cleaned_data.get("workout_assignment")
        workout_day = cleaned_data.get("workout_day")
        exercise = cleaned_data.get("exercise")

        if assignment and member and assignment.member_id != member.id:
            self.add_error("member", "Selected member must match the workout assignment member.")
        if assignment and workout_day and workout_day.workout_plan_id != assignment.workout_plan_id:
            self.add_error("workout_day", "Selected workout day must belong to the assignment plan.")
        if workout_day and exercise and not workout_day.exercises.filter(exercise_id=exercise.id).exists():
            self.add_error("exercise", "Selected exercise is not part of the chosen workout day.")
        return cleaned_data

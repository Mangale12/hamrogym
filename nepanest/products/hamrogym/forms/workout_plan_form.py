from django import forms

from ..models import WorkoutPlan


def _apply_bootstrap_widgets(form):
    for field in form.fields.values():
        widget = field.widget
        css_class = widget.attrs.get("class", "")
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs["class"] = "form-check-input"
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            widget.attrs["class"] = f"{css_class} form-select".strip()
        elif isinstance(widget, forms.DateInput):
            widget.attrs["class"] = f"{css_class} form-control".strip()
        elif isinstance(widget, forms.Textarea):
            widget.attrs["class"] = f"{css_class} form-control".strip()
            widget.attrs.setdefault("rows", 4)
        else:
            widget.attrs["class"] = f"{css_class} form-control".strip()


class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = [
            "name",
            "fitness_goal",
            "difficulty_level",
            "duration_week",
            "days_per_week",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Example: Fat Loss Starter Plan"}),
            "duration_week": forms.NumberInput(attrs={"min": 1}),
            "days_per_week": forms.NumberInput(attrs={"min": 1, "max": 7}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fitness_goal"].required = False
        self.fields["difficulty_level"].required = False
        self.fields["duration_week"].required = False
        self.fields["days_per_week"].required = False
        _apply_bootstrap_widgets(self)

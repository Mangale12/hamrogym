from django import forms

from ..models import Employee, LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = LeaveRequest
        fields = [
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "is_half_day",
            "half_day_type",
            "reason",
            "attachment",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = (
            lambda obj: f"{obj.employee_id} - {obj.full_name or obj.user.username}"
        )

from django import forms

from ..models import Employee, EmployeeShift


class EmployeeShiftForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = EmployeeShift
        fields = [
            "employee",
            "shift",
            "effective_from",
            "effective_to",
            "remarks",
        ]
        widgets = {
            "effective_from": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "effective_to": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = (
            lambda obj: f"{obj.employee_id} - {obj.full_name or obj.user.username}"
        )

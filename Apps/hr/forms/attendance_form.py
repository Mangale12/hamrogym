from django import forms

from ..models import AttendanceAdjustment, Employee


class AttendanceDashboardForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = []


class AttendanceAdjustmentForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())
    attendance_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = AttendanceAdjustment
        fields = [
            "employee",
            "attendance_date",
            "new_check_in",
            "new_check_out",
            "reason",
        ]
        widgets = {
            "new_check_in": forms.TimeInput(attrs={"type": "time"}),
            "new_check_out": forms.TimeInput(attrs={"type": "time"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = (
            lambda obj: f"{obj.employee_id} - {obj.full_name or obj.user.username}"
        )
        if self.instance.pk:
            self.fields["employee"].initial = self.instance.attendance.employee_id
            self.fields["attendance_date"].initial = self.instance.attendance.date

    def save(self, commit=True):
        return super().save(commit=commit)

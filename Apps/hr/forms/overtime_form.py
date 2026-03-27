from decimal import Decimal

from django import forms

from ..models import Employee, OvertimeRecord, OvertimeRequest


class OvertimeRequestForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = OvertimeRequest
        fields = [
            "employee",
            "overtime_date",
            "start_time",
            "end_time",
            "reason",
            "remarks",
        ]
        widgets = {
            "overtime_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = (
            lambda obj: f"{obj.employee_id} - {obj.full_name or obj.user.username}"
        )


class OvertimeRecordForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = OvertimeRecord
        fields = [
            "employee",
            "overtime_date",
            "start_time",
            "end_time",
            "overtime_hours",
            "overtime_rate",
            "overtime_amount",
            "status",
            "remarks",
        ]
        widgets = {
            "overtime_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "remarks": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = (
            lambda obj: f"{obj.employee_id} - {obj.full_name or obj.user.username}"
        )

    def clean(self):
        cleaned_data = super().clean()
        hours = cleaned_data.get("overtime_hours")
        rate = cleaned_data.get("overtime_rate")
        amount = cleaned_data.get("overtime_amount")
        if hours is not None and rate is not None and amount in (None, ""):
            cleaned_data["overtime_amount"] = Decimal(hours) * Decimal(rate)
        return cleaned_data

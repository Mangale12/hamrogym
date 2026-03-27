from django import forms

from ..models import Employee, LeaveAccrual, LeaveBalance, LeaveLedger


def _employee_label(obj):
    return f"{obj.employee_id} - {obj.full_name or obj.user.username}"


class LeaveBalanceForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = LeaveBalance
        fields = [
            "employee",
            "leave_type",
            "year",
            "opening_balance",
            "accrued",
            "used",
            "encashed",
            "balance",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = _employee_label


class LeaveLedgerForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = LeaveLedger
        fields = [
            "employee",
            "leave_type",
            "year",
            "change_type",
            "days",
            "reference_type",
            "reference_id",
            "balance_after",
            "remarks",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = _employee_label


class LeaveAccrualForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())

    class Meta:
        model = LeaveAccrual
        fields = [
            "employee",
            "leave_type",
            "policy",
            "accrual_date",
            "days_added",
            "remarks",
        ]
        widgets = {
            "accrual_date": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = _employee_label

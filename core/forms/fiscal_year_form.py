from django import forms

from core.models import FiscalYear

class FiscalYearForm(forms.ModelForm):
    class Meta:
        model = FiscalYear
        fields = ["name", "start_date", "end_date", "is_active", "is_current", "is_closed", "remarks"]

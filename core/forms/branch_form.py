from django import forms

from core.models import Branch


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ["organization", "name", "code", "is_active", "remarks"]

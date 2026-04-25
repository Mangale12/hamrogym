from django import forms

from nepanest.foundation.organization import Branch


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ["organization", "name", "code", "is_active", "remarks"]

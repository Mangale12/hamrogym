from django import forms

from ..models import ApprovalEntity


class ApprovalEntityForm(forms.ModelForm):
    class Meta:
        model = ApprovalEntity
        fields = [
            "erp_entity",
            "name",
            "code",
            "is_active",
            "remarks",
        ]

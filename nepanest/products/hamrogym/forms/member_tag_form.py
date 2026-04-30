from django import forms

from ..models import MemberTag


class MemberTagForm(forms.ModelForm):
    class Meta:
        model = MemberTag
        fields = [
            # TODO: add fields
            'name',
            'is_active',
            'remarks',
        ]

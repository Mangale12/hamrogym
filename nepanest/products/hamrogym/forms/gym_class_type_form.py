from django import forms

from nepanest.products.hamrogym.models.gym_class_type import GymClassType


class GymClassTypeForm(forms.ModelForm):
    class Meta:
        model = GymClassType
        fields = [
            "name",
            
            "is_active",
            "remarks",
        ]

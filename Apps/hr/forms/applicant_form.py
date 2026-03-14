from django import forms

from ..models import applicant


class applicantForm(forms.ModelForm):
    class Meta:
        model = applicant
        fields = [
            "name",
            "email",
            "phone",
            "date_of_birth",
            "gender",
            "marital_status",
            "status",
            "address",
            "country",
            "state",
            "city",
            "cv",
            "cover_letter",
            "date",
            "remarks",
        ]

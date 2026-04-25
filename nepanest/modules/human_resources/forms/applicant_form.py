from django import forms

from nepanest.modules.recruitment.models import Applicant


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
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

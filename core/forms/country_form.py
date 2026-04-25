from django import forms

from nepanest.foundation.geography import Country


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = [
            "name",
            "iso2",
            "iso3",
            "phone_code",
            "is_active",
            "remarks",
        ]

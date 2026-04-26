from django import forms

from ..models import Party, PartyIndividualProfile


class PartyForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    gender = forms.ChoiceField(
        choices=[("", "Select Gender"), *PartyIndividualProfile.GENDER_CHOICES],
        required=False,
    )
    photo = forms.ImageField(required=False)

    class Meta:
        model = Party
        fields = [
            "name",
            "display_name",
            "party_type",
            "category",
            "pan_number",
            "vat_number",
            "registration_number",
            "is_active",
            "remarks",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(self.instance, "individual_profile", None) if getattr(self.instance, "pk", None) else None
        if profile:
            self.initial.setdefault("date_of_birth", profile.date_of_birth)
            self.initial.setdefault("gender", profile.gender)
            self.initial.setdefault("photo", profile.photo)

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ["name", "display_name", "pan_number", "vat_number", "registration_number"]:
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()
        if cleaned_data.get("category") != "individual":
            cleaned_data["date_of_birth"] = None
            cleaned_data["gender"] = ""
        return cleaned_data

    def save(self, commit=True):
        party = super().save(commit=False)
        if not commit:
            return party

        party.save()
        self.save_m2m()

        if party.category == "individual":
            profile, _created = PartyIndividualProfile.objects.get_or_create(party=party)
            profile.date_of_birth = self.cleaned_data.get("date_of_birth")
            profile.gender = self.cleaned_data.get("gender", "")
            if "photo" in self.changed_data:
                profile.photo = self.cleaned_data.get("photo") or None
            profile.save()
        else:
            PartyIndividualProfile.objects.filter(party=party).delete()

        return party

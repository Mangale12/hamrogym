from django import forms

from core.models import Party, PartyIndividualProfile, PartyType

from ..models import Member, MemberProfile


class MemberForm(forms.ModelForm):
    party_name = forms.CharField(max_length=255, required=True)
    party_display_name = forms.CharField(max_length=255, required=False)
    party_type = forms.ModelChoiceField(
        queryset=PartyType.objects.order_by("name"),
        required=True,
    )
    pan_number = forms.CharField(max_length=50, required=False)
    vat_number = forms.CharField(max_length=50, required=False)
    registration_number = forms.CharField(max_length=100, required=False)
    party_is_active = forms.BooleanField(required=False, initial=True)
    party_remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    gender = forms.ChoiceField(
        choices=[("", "Select Gender"), *PartyIndividualProfile.GENDER_CHOICES],
        required=False,
    )
    photo = forms.ImageField(required=False)

    height = forms.DecimalField(required=False, max_digits=5, decimal_places=2)
    weight = forms.DecimalField(required=False, max_digits=5, decimal_places=2)
    fitness_goal = forms.ChoiceField(
        choices=[("", "Select Goal"), *MemberProfile.FITNESS_GOAL_CHOICES],
        required=False,
    )
    medical_conditions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = Member
        fields = [
            "member_code",
            "join_date",
            "status",
            "branch",
            "emergency_contact_name",
            "emergency_contact_phone",
            "remarks",
        ]
        widgets = {
            "join_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member_code"].required = False
        self.fields["branch"].required = True

        party = getattr(self.instance, "party", None) if getattr(self.instance, "pk", None) else None
        if party:
            self.initial.setdefault("party_name", party.name)
            self.initial.setdefault("party_display_name", party.display_name)
            self.initial.setdefault("party_type", party.party_type_id)
            self.initial.setdefault("pan_number", party.pan_number)
            self.initial.setdefault("vat_number", party.vat_number)
            self.initial.setdefault("registration_number", party.registration_number)
            self.initial.setdefault("party_is_active", party.is_active)
            self.initial.setdefault("party_remarks", party.remarks)

            party_profile = getattr(party, "individual_profile", None)
            if party_profile:
                self.initial.setdefault("date_of_birth", party_profile.date_of_birth)
                self.initial.setdefault("gender", party_profile.gender)
                self.initial.setdefault("photo", party_profile.photo)

        profile = getattr(self.instance, "profile", None) if getattr(self.instance, "pk", None) else None
        if profile:
            self.initial.setdefault("height", profile.height)
            self.initial.setdefault("weight", profile.weight)
            self.initial.setdefault("fitness_goal", profile.fitness_goal)
            self.initial.setdefault("medical_conditions", profile.medical_conditions)

    def clean(self):
        cleaned_data = super().clean()
        for field_name in [
            "party_name",
            "party_display_name",
            "pan_number",
            "vat_number",
            "registration_number",
            "party_remarks",
            "member_code",
            "emergency_contact_name",
            "emergency_contact_phone",
            "remarks",
            "medical_conditions",
        ]:
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()
        return cleaned_data

    def save(self, commit=True):
        member = super().save(commit=False)
        if not commit:
            return member

        party = getattr(member, "party", None)
        if party is None:
            party = Party(category="individual")

        party.name = self.cleaned_data.get("party_name")
        party.display_name = self.cleaned_data.get("party_display_name") or ""
        party.party_type = self.cleaned_data.get("party_type")
        party.category = "individual"
        party.pan_number = self.cleaned_data.get("pan_number") or ""
        party.vat_number = self.cleaned_data.get("vat_number") or ""
        party.registration_number = self.cleaned_data.get("registration_number") or ""
        party.is_active = bool(self.cleaned_data.get("party_is_active"))
        party.remarks = self.cleaned_data.get("party_remarks") or ""
        party.branch = self.cleaned_data.get("branch")
        if party.branch_id:
            party.organization_id = party.branch.organization_id
        party.save()

        member.party = party
        member.save()
        self.save_m2m()

        party_profile, _created = PartyIndividualProfile.objects.get_or_create(party=party)
        party_profile.date_of_birth = self.cleaned_data.get("date_of_birth")
        party_profile.gender = self.cleaned_data.get("gender", "")
        if "photo" in self.changed_data:
            party_profile.photo = self.cleaned_data.get("photo") or None
        party_profile.save()

        profile, _created = MemberProfile.objects.get_or_create(member=member)
        profile.height = self.cleaned_data.get("height")
        profile.weight = self.cleaned_data.get("weight")
        profile.fitness_goal = self.cleaned_data.get("fitness_goal", "")
        profile.medical_conditions = self.cleaned_data.get("medical_conditions", "")
        profile.save()
        return member

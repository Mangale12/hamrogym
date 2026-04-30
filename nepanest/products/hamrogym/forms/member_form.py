from django import forms
from django.db.models import Q
from django.utils.timezone import localdate

from core.models import Party, PartyIndividualProfile, PartyType

from ..models import ActivityLevel, FitnessGoal, Member, MemberProfile, MemberStatus


class MemberForm(forms.ModelForm):
    TAB_FIELDS = {
        "party": {
            "party_name",
            "party_display_name",
            "party_type",
            "pan_number",
            "vat_number",
            "registration_number",
            "party_is_active",
            "party_remarks",
        },
        "membership": {
            "member_code",
            "join_date",
            "status",
            "branch",
            "emergency_contact_name",
            "emergency_contact_phone",
            "remarks",
        },
        "profile": {
            "date_of_birth",
            "gender",
            "fitness_goals",
            "activity_level",
            "height",
            "weight",
            "bmi",
            "body_fat_percentage",
            "photo",
            "medical_conditions",
            "injuries",
        },
    }

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
    bmi = forms.DecimalField(required=False, max_digits=5, decimal_places=2)
    body_fat_percentage = forms.DecimalField(required=False, max_digits=5, decimal_places=2)
    activity_level = forms.ModelChoiceField(
        queryset=ActivityLevel.objects.filter(is_active=True).order_by("name"),
        required=False,
    )
    fitness_goals = forms.ModelMultipleChoiceField(
        queryset=FitnessGoal.objects.filter(is_active=True).order_by("name"),
        required=False,
        widget=forms.SelectMultiple,
    )
    medical_conditions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    injuries = forms.CharField(
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
            "activity_level",
            "height",
            "weight",
            "bmi",
            "body_fat_percentage",
            "medical_conditions",
            "injuries",
            "emergency_contact_name",
            "emergency_contact_phone",
            "remarks",
        ]
        widgets = {
            "join_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        self.active_tab = ((self.data.get("_active_tab") or "").strip() if self.is_bound else "") or None
        if self.active_tab:
            allowed_fields = self.TAB_FIELDS.get(self.active_tab, set())
            for name in list(self.fields.keys()):
                if name not in allowed_fields:
                    self.fields.pop(name)
        if "member_code" in self.fields:
            self.fields["member_code"].required = False
        if "branch" in self.fields:
            self.fields["branch"].required = True
        if "status" in self.fields:
            status_queryset = MemberStatus.objects.filter(is_active=True)
            if getattr(self.instance, "status_id", None):
                status_queryset = MemberStatus.objects.filter(Q(is_active=True) | Q(pk=self.instance.status_id))
            self.fields["status"].queryset = status_queryset.order_by("name")
            self.fields["status"].empty_label = "Select Status"
            self.fields["status"].required = True
            active_status = MemberStatus.objects.filter(code="active").first()
            if not getattr(self.instance, "pk", None) and active_status:
                self.initial.setdefault("status", active_status.pk)
        goal_queryset = FitnessGoal.objects.filter(is_active=True)
        profile = getattr(self.instance, "profile", None) if getattr(self.instance, "pk", None) else None
        if "fitness_goals" in self.fields:
            selected_goal_ids = []
            if profile:
                selected_goal_ids = list(profile.fitness_goals.values_list("pk", flat=True))
            if selected_goal_ids:
                goal_queryset = FitnessGoal.objects.filter(Q(is_active=True) | Q(pk__in=selected_goal_ids))
            self.fields["fitness_goals"].queryset = goal_queryset.order_by("name")
        if "activity_level" in self.fields:
            activity_level_queryset = ActivityLevel.objects.filter(is_active=True)
            if getattr(self.instance, "activity_level_id", None):
                activity_level_queryset = ActivityLevel.objects.filter(
                    Q(is_active=True) | Q(pk=self.instance.activity_level_id)
                )
            self.fields["activity_level"].queryset = activity_level_queryset.order_by("name")
            self.fields["activity_level"].empty_label = "Select Activity Level"

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

        if profile:
            self.initial.setdefault("height", self.instance.height or profile.height)
            self.initial.setdefault("weight", self.instance.weight or profile.weight)
            self.initial.setdefault("fitness_goals", list(profile.fitness_goals.values_list("pk", flat=True)))
            self.initial.setdefault("medical_conditions", self.instance.medical_conditions or profile.medical_conditions)

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
            "injuries",
        ]:
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()
        if self.active_tab == "party" and not self.instance.pk:
            cleaned_data.setdefault("join_date", localdate())
        return cleaned_data

    def save(self, commit=True):
        member = super().save(commit=False)
        self._apply_party_values(member)
        if self.active_tab == "party" and not member.join_date:
            member.join_date = localdate()
        if commit:
            self.prepare_related(member)
            member.save()
            self.save_related(member)
        return member

    def _apply_party_values(self, member):
        party = getattr(member, "party", None)
        if party is None:
            party = Party(category="individual")

        if "party_name" in self.cleaned_data:
            party.name = self.cleaned_data.get("party_name")
        if "party_display_name" in self.cleaned_data:
            party.display_name = self.cleaned_data.get("party_display_name") or ""
        if "party_type" in self.cleaned_data:
            party.party_type = self.cleaned_data.get("party_type")
        party.category = "individual"
        if "pan_number" in self.cleaned_data:
            party.pan_number = self.cleaned_data.get("pan_number") or ""
        if "vat_number" in self.cleaned_data:
            party.vat_number = self.cleaned_data.get("vat_number") or ""
        if "registration_number" in self.cleaned_data:
            party.registration_number = self.cleaned_data.get("registration_number") or ""
        if "party_is_active" in self.cleaned_data:
            party.is_active = bool(self.cleaned_data.get("party_is_active"))
        if "party_remarks" in self.cleaned_data:
            party.remarks = self.cleaned_data.get("party_remarks") or ""
        if "branch" in self.cleaned_data:
            party.branch = self.cleaned_data.get("branch")
        if party.branch_id:
            party.organization_id = party.branch.organization_id
        member.party = party
        return party

    def prepare_related(self, member=None):
        member = member or self.instance
        if member is None:
            return
        party = self._apply_party_values(member)
        if not party.name:
            self.add_error("party_name", "This field is required.")
            return
        if not getattr(party, "party_type_id", None):
            self.add_error("party_type", "This field is required.")
            return
        party.save()
        member.party = party

    def save_related(self, member=None):
        member = member or self.instance
        if not member or not member.pk:
            return

        party = getattr(member, "party", None)
        if party and member.branch_id and not party.branch_id:
            party.branch = member.branch
            party.organization_id = member.branch.organization_id
            party.save(update_fields=["branch", "organization", "updated_at"])

        if not self.active_tab or self.active_tab == "profile":
            party_profile, _created = PartyIndividualProfile.objects.get_or_create(party=party)
            if "date_of_birth" in self.cleaned_data:
                party_profile.date_of_birth = self.cleaned_data.get("date_of_birth")
            if "gender" in self.cleaned_data:
                party_profile.gender = self.cleaned_data.get("gender", "")
            if "photo" in self.changed_data:
                party_profile.photo = self.cleaned_data.get("photo") or None
            party_profile.save()

            profile, _created = MemberProfile.objects.get_or_create(member=member)
            if "height" in self.cleaned_data:
                profile.height = self.cleaned_data.get("height")
            if "weight" in self.cleaned_data:
                profile.weight = self.cleaned_data.get("weight")
            if "medical_conditions" in self.cleaned_data:
                profile.medical_conditions = self.cleaned_data.get("medical_conditions") or ""
            profile.save()
            if "fitness_goals" in self.cleaned_data:
                profile.fitness_goals.set(self.cleaned_data.get("fitness_goals"))

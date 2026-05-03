from django import forms
from django.db.models import Q

from nepanest.modules.people.models import Employee

from ..models import (
    Member,
    MemberCheckin,
    MemberPTPackage,
    PTSession,
    PTSessionCancellation,
    PTSessionLog,
    PTSessionPackage,
    PTSessionReschedule,
    Trainer,
    TrainerAvailability,
    TrainerPerformance,
    TrainerTimeOff,
)


def _include_current(base_queryset, current_id):
    if current_id:
        return base_queryset.model.objects.filter(Q(pk=current_id) | Q(pk__in=base_queryset.values("pk")))
    return base_queryset


class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = [
            "employee",
            "specialization",
            "experience_years",
            "certification_details",
            "max_sessions_per_day",
            "rating",
            "status",
            "notes",
            "remarks",
        ]
        widgets = {
            "certification_details": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Employee.objects.filter(is_active=True)
        queryset = _include_current(queryset, getattr(self.instance, "employee_id", None))
        self.fields["employee"].queryset = queryset.order_by("employee_id")


class TrainerAvailabilityForm(forms.ModelForm):
    class Meta:
        model = TrainerAvailability
        fields = [
            "trainer",
            "day_of_week",
            "start_time",
            "end_time",
            "is_available",
            "remarks",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Trainer.objects.filter(status=Trainer.Status.ACTIVE)
        queryset = _include_current(queryset, getattr(self.instance, "trainer_id", None))
        self.fields["trainer"].queryset = queryset.order_by("employee__employee_id")


class TrainerTimeOffForm(forms.ModelForm):
    class Meta:
        model = TrainerTimeOff
        fields = [
            "trainer",
            "start_date",
            "end_date",
            "reason",
            "remarks",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Trainer.objects.filter(status=Trainer.Status.ACTIVE)
        queryset = _include_current(queryset, getattr(self.instance, "trainer_id", None))
        self.fields["trainer"].queryset = queryset.order_by("employee__employee_id")


class PTSessionPackageForm(forms.ModelForm):
    class Meta:
        model = PTSessionPackage
        fields = [
            "name",
            "total_sessions",
            "validity_days",
            "session_duration_minutes",
            "description",
            "status",
            "branch",
            "remarks",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }


class MemberPTPackageForm(forms.ModelForm):
    class Meta:
        model = MemberPTPackage
        fields = [
            "member",
            "pt_session_package",
            "total_sessions",
            "used_sessions",
            "remaining_sessions",
            "start_date",
            "end_date",
            "status",
            "remarks",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        member_queryset = Member.objects.all()
        member_queryset = _include_current(member_queryset, getattr(self.instance, "member_id", None))
        self.fields["member"].queryset = member_queryset.order_by("member_code")

        package_queryset = PTSessionPackage.objects.filter(status=PTSessionPackage.Status.ACTIVE)
        package_queryset = _include_current(package_queryset, getattr(self.instance, "pt_session_package_id", None))
        self.fields["pt_session_package"].queryset = package_queryset.order_by("name")


class PTSessionForm(forms.ModelForm):
    class Meta:
        model = PTSession
        fields = [
            "member",
            "trainer",
            "member_pt_package",
            "session_date",
            "start_time",
            "end_time",
            "status",
            "checkin",
            "notes",
            "remarks",
        ]
        widgets = {
            "session_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        member_queryset = Member.objects.all()
        member_queryset = _include_current(member_queryset, getattr(self.instance, "member_id", None))
        self.fields["member"].queryset = member_queryset.order_by("member_code")

        trainer_queryset = Trainer.objects.filter(status=Trainer.Status.ACTIVE)
        trainer_queryset = _include_current(trainer_queryset, getattr(self.instance, "trainer_id", None))
        self.fields["trainer"].queryset = trainer_queryset.order_by("employee__employee_id")

        package_queryset = MemberPTPackage.objects.all()
        package_queryset = _include_current(package_queryset, getattr(self.instance, "member_pt_package_id", None))
        self.fields["member_pt_package"].queryset = package_queryset.order_by("-start_date", "-id")

        checkin_queryset = MemberCheckin.objects.all()
        checkin_queryset = _include_current(checkin_queryset, getattr(self.instance, "checkin_id", None))
        self.fields["checkin"].queryset = checkin_queryset.order_by("-checkin_time", "-id")


class PTSessionLogForm(forms.ModelForm):
    class Meta:
        model = PTSessionLog
        fields = [
            "pt_session",
            "actual_start_time",
            "actual_end_time",
            "duration_minutes",
            "trainer_notes",
            "member_feedback",
            "remarks",
        ]
        widgets = {
            "actual_start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "actual_end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "trainer_notes": forms.Textarea(attrs={"rows": 3}),
            "member_feedback": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = PTSession.objects.exclude(execution_log__isnull=False)
        if getattr(self.instance, "pt_session_id", None):
            queryset = PTSession.objects.filter(Q(execution_log__isnull=True) | Q(pk=self.instance.pt_session_id))
        self.fields["pt_session"].queryset = queryset.order_by("-session_date", "start_time", "-id")


class PTSessionRescheduleForm(forms.ModelForm):
    class Meta:
        model = PTSessionReschedule
        fields = [
            "pt_session",
            "old_date",
            "old_start_time",
            "new_date",
            "new_start_time",
            "reason",
            "remarks",
        ]
        widgets = {
            "old_date": forms.DateInput(attrs={"type": "date"}),
            "new_date": forms.DateInput(attrs={"type": "date"}),
            "old_start_time": forms.TimeInput(attrs={"type": "time"}),
            "new_start_time": forms.TimeInput(attrs={"type": "time"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = PTSession.objects.exclude(status=PTSession.Status.CANCELLED)
        queryset = _include_current(queryset, getattr(self.instance, "pt_session_id", None))
        self.fields["pt_session"].queryset = queryset.order_by("-session_date", "start_time", "-id")


class PTSessionCancellationForm(forms.ModelForm):
    class Meta:
        model = PTSessionCancellation
        fields = [
            "pt_session",
            "cancelled_by",
            "reason",
            "cancellation_time",
            "remarks",
        ]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 3}),
            "cancellation_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = PTSession.objects.exclude(cancellation__isnull=False)
        if getattr(self.instance, "pt_session_id", None):
            queryset = PTSession.objects.filter(Q(cancellation__isnull=True) | Q(pk=self.instance.pt_session_id))
        self.fields["pt_session"].queryset = queryset.order_by("-session_date", "start_time", "-id")


class TrainerPerformanceForm(forms.ModelForm):
    class Meta:
        model = TrainerPerformance
        fields = [
            "trainer",
            "date",
            "total_sessions",
            "completed_sessions",
            "cancelled_sessions",
            "remarks",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Trainer.objects.all()
        queryset = _include_current(queryset, getattr(self.instance, "trainer_id", None))
        self.fields["trainer"].queryset = queryset.order_by("employee__employee_id")

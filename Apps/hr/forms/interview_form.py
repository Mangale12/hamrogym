from datetime import datetime

from django import forms

from ..models import Interview, InterviewStage


class InterviewForm(forms.ModelForm):
    scheduled_date = forms.DateField(required=True)
    scheduled_time = forms.TimeField(required=True)

    class Meta:
        model = Interview
        fields = [
            "job_application",
            "interview_stage",
            "location",
            "mode",
            "status",
            "is_active",
            "remarks",
        ]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type": "date"}),
            "scheduled_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interview_stage"].queryset = (
            self.fields["interview_stage"].queryset.filter(is_active=True).order_by("sequence", "name")
        )
        self.fields["job_application"].queryset = (
            self.fields["job_application"].queryset.select_related("applicant", "job_posting")
        )

        if self.instance.pk and self.instance.scheduled_at:
            self.initial["scheduled_date"] = self.instance.scheduled_at.date()
            self.initial["scheduled_time"] = self.instance.scheduled_at.strftime("%H:%M")

    def clean(self):
        cleaned_data = super().clean()
        job_application = cleaned_data.get("job_application")
        interview_stage = cleaned_data.get("interview_stage")
        scheduled_date = cleaned_data.get("scheduled_date")
        scheduled_time = cleaned_data.get("scheduled_time")

        if scheduled_date and scheduled_time:
            cleaned_data["scheduled_at"] = datetime.combine(scheduled_date, scheduled_time)

        if not job_application or not interview_stage:
            return cleaned_data

        interviews = (
            Interview.objects.filter(job_application=job_application)
            .exclude(pk=self.instance.pk)
            .select_related("interview_stage")
        )

        if interviews.filter(interview_stage=interview_stage).exists():
            self.add_error(
                "interview_stage",
                "This interview stage is already recorded for the selected job application.",
            )

        missing_previous_stage = InterviewStage.objects.filter(
            sequence__lt=interview_stage.sequence,
            is_active=True,
        ).exclude(
            interviews__job_application=job_application,
        ).exists()
        if missing_previous_stage:
            self.add_error(
                "interview_stage",
                "Create the earlier interview stage before scheduling this round.",
            )

        later_stage_exists = interviews.filter(
            interview_stage__sequence__gt=interview_stage.sequence
        ).exists()
        if later_stage_exists:
            self.add_error(
                "interview_stage",
                "A later interview stage already exists for this application.",
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.scheduled_at = self.cleaned_data["scheduled_at"]
        if commit:
            instance.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return instance

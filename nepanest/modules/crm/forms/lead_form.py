from django import forms


from ..models import Lead, Inquiry, FollowUp


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "name",
            "email",
            "phone",
            "company_name",
            "lead_source",
            "lead_status",
            "assigned_to",
            "service",
            "budget",
            "last_contacted",
            "next_followup",
            "party",
        ]


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = [
            "lead",
            "date",
            "message",
            "priority",
            "subject",
        ]

class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = [
            "lead",
            "followup_date",
            "next_followup_date",
            "discussion",
            "is_completed",
        ]

from django import forms

from ..models import JobOffer, JobOfferAttachment


class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = [
            "job_application",
            "offer_date",
            "salary_offered",
            "joining_date",
            "status",
            "remarks",
        ]
        widgets = {
            "offer_date": forms.DateInput(attrs={"type": "date"}),
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "salary_offered": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }


class JobOfferAttachmentForm(forms.ModelForm):
    class Meta:
        model = JobOfferAttachment
        fields = [
            "job_offer",
            "file",
            "document_type",
        ]

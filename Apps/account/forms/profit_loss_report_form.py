from django import forms
from django.utils import timezone

from core.models import Branch, FiscalYear, Organization


class ProfitLossReportForm(forms.Form):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.filter(is_active=True).order_by("name"),
        required=False,
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.filter(is_active=True).select_related("organization").order_by(
            "organization__name",
            "name",
        ),
        required=False,
    )
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.filter(is_active=True).order_by("-start_date", "-id"),
        required=False,
    )
    date_from = forms.DateField(required=True)
    date_to = forms.DateField(required=True)
    show_zero_balances = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["date_from"].initial = today.replace(day=1)
        self.fields["date_to"].initial = today
        self.fields["organization"].empty_label = "All Organizations"
        self.fields["branch"].empty_label = "All Branches"
        self.fields["fiscal_year"].empty_label = "All Fiscal Years"

    def clean(self):
        cleaned_data = super().clean()
        organization = cleaned_data.get("organization")
        branch = cleaned_data.get("branch")
        fiscal_year = cleaned_data.get("fiscal_year")
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if branch and organization and branch.organization_id != organization.pk:
            self.add_error("branch", "Selected branch does not belong to the selected organization.")

        if branch and not organization:
            cleaned_data["organization"] = branch.organization

        if date_from and date_to and date_from > date_to:
            self.add_error("date_to", "Date to must be greater than or equal to date from.")

        if fiscal_year and date_from and date_to:
            if date_from < fiscal_year.start_date or date_from > fiscal_year.end_date:
                self.add_error(
                    "date_from",
                    f"Date from must be between {fiscal_year.start_date} and {fiscal_year.end_date} for {fiscal_year}.",
                )
            if date_to < fiscal_year.start_date or date_to > fiscal_year.end_date:
                self.add_error(
                    "date_to",
                    f"Date to must be between {fiscal_year.start_date} and {fiscal_year.end_date} for {fiscal_year}.",
                )

        return cleaned_data

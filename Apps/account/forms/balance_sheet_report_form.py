from django import forms
from django.utils import timezone

from core.models import Branch, FiscalYear, Organization


class BalanceSheetReportForm(forms.Form):
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
    as_of_date = forms.DateField(required=True)
    show_zero_balances = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["as_of_date"].initial = timezone.localdate()
        self.fields["organization"].empty_label = "All Organizations"
        self.fields["branch"].empty_label = "All Branches"
        self.fields["fiscal_year"].empty_label = "All Fiscal Years"

    def clean(self):
        cleaned_data = super().clean()
        organization = cleaned_data.get("organization")
        branch = cleaned_data.get("branch")
        fiscal_year = cleaned_data.get("fiscal_year")
        as_of_date = cleaned_data.get("as_of_date")

        if branch and organization and branch.organization_id != organization.pk:
            self.add_error("branch", "Selected branch does not belong to the selected organization.")

        if branch and not organization:
            cleaned_data["organization"] = branch.organization

        if fiscal_year and as_of_date:
            if as_of_date < fiscal_year.start_date or as_of_date > fiscal_year.end_date:
                self.add_error(
                    "as_of_date",
                    f"As of date must be between {fiscal_year.start_date} and {fiscal_year.end_date} for {fiscal_year}.",
                )

        return cleaned_data

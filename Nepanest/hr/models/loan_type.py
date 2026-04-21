from django.db import models
from django.core.exceptions import ValidationError

from core.choices import INTEREST_TYPE_CHOICES

class LoanType(models.Model):
    

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, unique=True)
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPE_CHOICES)

    default_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Default interest rate (%)")

    max_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maximum allowed loan amount")

    max_tenure_months = models.IntegerField()
    min_tenure_months = models.IntegerField(default=1)

    requires_approval = models.BooleanField(default=True)
    requires_guarantor = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.min_tenure_months > self.max_tenure_months:
            raise ValidationError("Min tenure cannot be greater than max tenure")

        if self.default_interest_rate < 0:
            raise ValidationError("Interest rate cannot be negative")

    def __str__(self):
        return f"{self.name} ({self.code})"


class LoanPolicy(models.Model):
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE, related_name="policies")

    employment_type = models.ForeignKey("EmploymentType", on_delete=models.CASCADE, related_name="loan_policies")

    # Eligibility
    max_eligible_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # EMI / Installment
    max_installment_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Tenure Rules
    max_tenure_months = models.IntegerField()
    min_tenure_months = models.IntegerField(default=1)

    # Interest Override (optional)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Override LoanType interest rate")

    # Constraints
    grace_period_days = models.IntegerField(default=0)
    min_credit_score = models.IntegerField(null=True, blank=True)

    # Salary-based Rules
    max_loan_percentage_of_salary = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    max_emi_percentage_of_salary = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # System Fields
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "employment_type__name", "id"]
        unique_together = ("loan_type", "employment_type")

    def clean(self):
        if self.min_tenure_months > self.max_tenure_months:
            raise ValidationError("Min tenure cannot be greater than max tenure")

        if self.grace_period_days < 0:
            raise ValidationError("Grace period cannot be negative")

        if self.min_credit_score is not None and self.min_credit_score < 0:
            raise ValidationError("Credit score cannot be negative")

        if self.max_loan_percentage_of_salary is not None and self.max_loan_percentage_of_salary < 0:
            raise ValidationError("Loan % of salary cannot be negative")

        if self.max_loan_percentage_of_salary is not None and self.max_loan_percentage_of_salary > 100:
            raise ValidationError("Loan % of salary cannot exceed 100")

        if self.max_emi_percentage_of_salary is not None and self.max_emi_percentage_of_salary < 0:
            raise ValidationError("EMI % of salary cannot be negative")

        if self.max_emi_percentage_of_salary is not None and self.max_emi_percentage_of_salary > 100:
            raise ValidationError("EMI % of salary cannot exceed 100")

        if self.interest_rate is not None and self.interest_rate < 0:
            raise ValidationError("Interest rate cannot be negative")

    def get_effective_interest_rate(self):
        """
        Returns policy interest if defined, otherwise fallback to LoanType default
        """
        return self.interest_rate if self.interest_rate is not None else self.loan_type.default_interest_rate

    def __str__(self):
        return f"{self.loan_type.name} - {self.employment_type.name}"

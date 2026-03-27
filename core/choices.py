GENDER_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
]

MARITAL_STATUS_CHOICES = [
    ("single", "Single"),
    ("married", "Married"),
]

BLOOD_GROUP_CHOICES = [
    ("A+", "A+"),
    ("A-", "A-"),
    ("B+", "B+"),
    ("B-", "B-"),
    ("AB+", "AB+"),
    ("AB-", "AB-"),
    ("O+", "O+"),
    ("O-", "O-"),
]

NATIONALITY_CHOICES = [
    ("nepali", "Nepali"),
    ("indian", "Indian"),
    ("chinese", "Chinese"),
    ("bhutanese", "Bhutanese"),
    ("bangladeshi", "Bangladeshi"),
    ("pakistani", "Pakistani"),
    ("sri_lankan", "Sri Lankan"),
    ("other", "Other"),
]

RELIGION_CHOICES = [
    ("hindu", "Hindu"),
    ("buddhist", "Buddhist"),
    ("islam", "Islam"),
    ("christian", "Christian"),
    ("sikh", "Sikh"),
    ("jain", "Jain"),
    ("other", "Other"),
]

APPLICANT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("shortlisted", "Shortlisted"),
    ("interviewed", "Interviewed"),
    ("selected", "Selected"),
    ("hired", "Hired"),
    ("rejected", "Rejected"),
]

JOB_APPLICATION_STATUS_CHOICES = [
    ("applied", "Applied"),
    ("shortlisted", "Shortlisted"),
    ("interview_scheduled", "Interview Scheduled"),
    ("interviewed", "Interviewed"),
    ("selected", "Selected"),
    ("hired", "Hired"),
    ("rejected", "Rejected"),
    ("withdrawn", "Withdrawn"),
]

EMPLOYEE_TYPE_CHOICES = [
    ("full_time", "Full time"),
    ("part_time", "Part time"),
    ("contract", "Contract"),
]

EMPLOYMENT_STATUS_CHOICES = [
    ("active", "Active"),
    ("resigned", "Resigned"),
    ("terminated", "Terminated"),
]

PAYMENT_METHOD_CHOICES = [
    ("cash", "Cash"),
    ("bank", "Bank"),
]

SALARY_TYPE_CHOICES = [
    ("monthly", "Monthly"),
    ("hourly", "Hourly"),
]

PAYMENT_FREQUENCY_CHOICES = [
    ("monthly", "Monthly"),
    ("biweekly", "Biweekly"),
    ("weekly", "Weekly"),
]

WORK_LOCATION_CHOICES = [
    ("office", "Office"),
    ("branch", "Branch"),
]

JOB_REQUISITION_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("cancelled", "Cancelled"),
]

APPROVAL_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("cancelled", "Cancelled"),
]

RECRUITMENT_REASON_CHOICES = [
    ("replacement", "Replacement"),
    ("new_position", "New Position"),
    ("expansion", "Expansion"),
]


PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]


SCREENING_QUESTION_TYPE_CHOICES = [
    ("multiple_choice", "Multiple Choice"),
    ("text", "Text"),
    ("yes_no", "Yes/No"),
]

INTERVIEW_MODE_CHOICES = [
    ("in_person", "In Person"),
    ("video", "Video"),
    ("phone", "Phone"),
]

INTERVIEW_STATUS_CHOICES = [
    ("scheduled", "Scheduled"),
    ("in_progress", "In Progress"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

INTERVIEW_FEEDBACK_RECOMMENDATIONS_CHOICES = [
    ("hire", "Hire"),
    ("reject", "Reject"),
    ("next_round", "Next Round"),
]

ATTENDANCE_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("present", "Present"),
    ("absent", "Absent"),
    ("late", "Late"),
    ("half_day", "Half Day"),
    ("leave", "Leave"),
]

ATTENDANCE_ADJUSTMENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


MODULE_CHOICES = [
    ("attendance", "Attendance"),
    ("leave", "Leave"),
    ("overtime", "Overtime"),
    ("payroll", "Payroll"),
    ("inventory", "Inventory"),
    ("sales", "Sales"),
]

WEEKDAY_CHOICES = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]

LEAVE_ACCRUAL_TYPE_CHOICES = [
    ("monthly", "Monthly"),
    ("yearly", "Yearly"),
]

LEAVE_HALF_DAY_TYPE_CHOICES = [
    ("first_half", "First Half"),
    ("second_half", "Second Half"),
]

LEAVE_LEDGER_CHANGE_TYPE_CHOICES = [
    ("opening", "Opening"),
    ("accrual", "Accrual"),
    ("leave_approved", "Leave Approved"),
    ("leave_cancelled", "Leave Cancelled"),
    ("leave_rejected", "Leave Rejected"),
    ("encashment", "Encashment"),
    ("carry_forward", "Carry Forward"),
    ("adjustment", "Adjustment"),
    ("compoff_earned", "Comp Off Earned"),
    ("compoff_used", "Comp Off Used"),
]

PAYROLL_COMPONENT_TYPE_CHOICES = [
    ("earning", "Earning"),
    ("deduction", "Deduction"),
    ("employer_contribution", "Employer Contribution"),
    ("information", "Information"),
]

PAYROLL_COMPONENT_VALUE_TYPE_CHOICES = [
    ("fixed", "Fixed"),
    ("percentage", "Percentage"),
    ("formula", "Formula"),
]

PAYROLL_TAX_TREATMENT_CHOICES = [
    ("taxable", "Taxable"),
    ("non_taxable", "Non Taxable"),
    ("tax_exempt", "Tax Exempt"),
]

PAYROLL_ROUNDING_RULE_CHOICES = [
    ("round_2", "Round 2 Decimals"),
    ("round_0", "Round Whole Number"),
    ("ceil", "Ceil"),
    ("floor", "Floor"),
]

PAYROLL_RUN_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("processed", "Processed"),
    ("reviewed", "Reviewed"),
    ("approved", "Approved"),
    ("locked", "Locked"),
]

PAYROLL_RUN_EMPLOYEE_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("processed", "Processed"),
    ("error", "Error"),
]

PAYROLL_COMPONENT_SOURCE_TYPE_CHOICES = [
    ("structure", "Structure"),
    ("override", "Override"),
    ("adjustment", "Adjustment"),
    ("attendance", "Attendance"),
    ("leave", "Leave"),
    ("overtime", "Overtime"),
    ("tax", "Tax"),
    ("statutory", "Statutory"),
]

PAYROLL_ADJUSTMENT_TYPE_CHOICES = [
    ("earning", "Earning"),
    ("deduction", "Deduction"),
    ("arrear", "Arrear"),
    ("bonus", "Bonus"),
    ("correction", "Correction"),
]


INTEREST_TYPE_CHOICES = [
        ("flat", "Flat"),
        ("reducing", "Reducing"),
        ("none", "No Interest"),
    ]

LOAN_APPLICATION_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("cancelled", "Cancelled"),
]

LOAN_ACCOUNT_STATUS_CHOICES = [
    ("active", "Active"),
    ("closed", "Closed"),
    ("defaulted", "Defaulted"),
]

LOAN_INSTALLMENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("partial", "Partial"),
    ("paid", "Paid"),
    ("overdue", "Overdue"),
]

LOAN_ADJUSTMENT_TYPE_CHOICES = [
    ("waiver", "Waiver"),
    ("penalty", "Penalty"),
    ("extra_payment", "Extra Payment"),
]

LOAN_LEDGER_TRANSACTION_TYPE_CHOICES = [
    ("disbursement", "Disbursement"),
    ("repayment", "Repayment"),
    ("adjustment", "Adjustment"),
    ("penalty", "Penalty"),
    ("closure", "Closure"),
    ("payroll_deduction", "Payroll Deduction"),
]

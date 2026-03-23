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
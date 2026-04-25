from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.choices import BLOOD_GROUP_CHOICES
from nepanest.foundation.geography import Country, State

from nepanest.modules.people.models import (
    Employee,
    EmployeeAccess,
    EmployeeAddress,
    EmployeeAttendance,
    EmployeeBank,
    EmployeeContact,
    EmployeeEmergency,
    EmployeeExit,
    EmployeeLegal,
    EmployeePayroll,
    EmployeeProfile,
    EmployeeWork,
)


User = get_user_model()


class EmployeeForm(forms.ModelForm):
    TAB_FIELDS = {
        "basic": [
            "employee_id",
            "employee_code",
            "username",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "password",
            "gender",
            "date_of_birth",
            "nationality",
            "marital_status",
            "blood_group",
            "profile_photo",
        ],
        "contact": ["phone", "alternate_phone"],
        "address": [
            "address",
            "permanent_address",
            "city",
            "state",
            "country",
            "zip_code",
        ],
        "employment": [
            "organization",
            "branch",
            "department",
            "designation",
            "reporting_manager",
            "join_date",
            "employee_type",
            "employment_status",
            "shift",
            "probation_period",
            "is_active",
            "remarks",
        ],
        "payroll": [
            "salary_type",
            "basic_salary",
            "allowance",
            "overtime_rate",
            "tax_number",
        ],
        "bank": [
            "bank_name",
            "bank_account_number",
            "bank_branch",
            "payment_method",
        ],
        "legal": [
            "citizenship_no",
            "passport_no",
            "pan_no",
            "social_security_no",
            "insurance_no",
        ],
        "work": [
            "job_description",
            "work_location",
            "work_email",
            "joining_letter",
            "contract_file",
        ],
        "attendance": ["attendance_required", "leave_group", "weekly_off"],
        "emergency": [
            "emergency_contact_name",
            "relationship",
            "emergency_phone",
            "emergency_address",
        ],
        "access": ["role", "permission_group", "login_enabled"],
        "exit": [
            "resignation_date",
            "last_working_date",
            "exit_reason",
            "exit_notes",
            "remarks",
        ],
        "documents": [],
    }

    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    password = forms.CharField(
        required=False, widget=forms.PasswordInput(render_value=False)
    )

    middle_name = forms.CharField(max_length=50, required=False)
    gender = forms.ChoiceField(choices=EmployeeProfile.GENDER_CHOICES, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    nationality = forms.ModelChoiceField(queryset=Country.objects.all(), required=False)
    marital_status = forms.ChoiceField(choices=EmployeeProfile.MARITAL_STATUS_CHOICES, required=False)
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    profile_photo = forms.FileField(required=False)

    phone = forms.CharField(max_length=30, required=False)
    alternate_phone = forms.CharField(max_length=30, required=False)

    address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    permanent_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    city = forms.CharField(max_length=100, required=False)
    state = forms.ModelChoiceField(queryset=State.objects.all(), required=False)
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False)
    zip_code = forms.CharField(max_length=20, required=False)

    salary_type = forms.ChoiceField(choices=EmployeePayroll.SALARY_TYPE_CHOICES, required=False)
    basic_salary = forms.DecimalField(required=False, max_digits=12, decimal_places=2)
    allowance = forms.DecimalField(required=False, max_digits=12, decimal_places=2)
    overtime_rate = forms.DecimalField(required=False, max_digits=12, decimal_places=2)
    tax_number = forms.CharField(max_length=50, required=False)

    bank_name = forms.CharField(max_length=100, required=False)
    bank_account_number = forms.CharField(max_length=50, required=False)
    bank_branch = forms.CharField(max_length=100, required=False)
    payment_method = forms.ChoiceField(choices=EmployeeBank.PAYMENT_METHOD_CHOICES, required=False)

    citizenship_no = forms.CharField(max_length=50, required=False)
    passport_no = forms.CharField(max_length=50, required=False)
    pan_no = forms.CharField(max_length=50, required=False)
    social_security_no = forms.CharField(max_length=50, required=False)
    insurance_no = forms.CharField(max_length=50, required=False)

    job_description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    work_location = forms.ChoiceField(choices=EmployeeWork.WORK_LOCATION_CHOICES, required=False)
    work_email = forms.EmailField(required=False)
    joining_letter = forms.FileField(required=False)
    contract_file = forms.FileField(required=False)

    attendance_required = forms.BooleanField(required=False)
    leave_group = forms.CharField(max_length=100, required=False)
    weekly_off = forms.CharField(max_length=50, required=False)

    emergency_contact_name = forms.CharField(max_length=100, required=False)
    relationship = forms.CharField(max_length=50, required=False)
    emergency_phone = forms.CharField(max_length=30, required=False)
    emergency_address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    role = forms.CharField(max_length=100, required=False)
    permission_group = forms.CharField(max_length=100, required=False)
    login_enabled = forms.BooleanField(required=False)

    resignation_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    last_working_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    exit_reason = forms.CharField(max_length=255, required=False)
    exit_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = Employee
        fields = [
            "organization",
            "branch",
            "employee_id",
            "employee_code",
            "department",
            "designation",
            "reporting_manager",
            "join_date",
            "employee_type",
            "employment_status",
            "shift",
            "probation_period",
            "is_active",
            "remarks",
        ]
        widgets = {
            "join_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_tab = (self.data.get("_active_tab") or "").strip() or None
        if self.active_tab:
            allowed = set(self.TAB_FIELDS.get(self.active_tab, []))
            for name in list(self.fields.keys()):
                if name not in allowed:
                    self.fields.pop(name)
        self._apply_required_rules()

        user = getattr(self.instance, "user", None)
        if user:
            self.initial.setdefault("username", user.username)
            self.initial.setdefault("email", user.email)
            self.initial.setdefault("first_name", user.first_name)
            self.initial.setdefault("last_name", user.last_name)

        self._set_related_initial("profile", EmployeeProfile, [
            "middle_name",
            "gender",
            "date_of_birth",
            "nationality",
            "marital_status",
            "blood_group",
        ])
        self._set_related_initial("contact", EmployeeContact, [
            "phone",
            "alternate_phone",
        ])
        self._set_related_initial("address", EmployeeAddress, [
            "address",
            "permanent_address",
            "city",
            "state",
            "country",
            "zip_code",
        ])
        self._set_related_initial("payroll", EmployeePayroll, [
            "salary_type",
            "basic_salary",
            "allowance",
            "overtime_rate",
            "tax_number",
        ])
        self._set_related_initial("bank", EmployeeBank, [
            "bank_name",
            "bank_account_number",
            "bank_branch",
            "payment_method",
        ])
        self._set_related_initial("legal", EmployeeLegal, [
            "citizenship_no",
            "passport_no",
            "pan_no",
            "social_security_no",
            "insurance_no",
        ])
        self._set_related_initial("work", EmployeeWork, [
            "job_description",
            "work_location",
            "work_email",
        ])
        self._set_related_initial("attendance", EmployeeAttendance, [
            "attendance_required",
            "leave_group",
            "weekly_off",
        ])
        self._set_related_initial("emergency", EmployeeEmergency, [
            "emergency_contact_name",
            "relationship",
            "emergency_phone",
            "emergency_address",
        ])
        self._set_related_initial("access", EmployeeAccess, [
            "role",
            "permission_group",
            "login_enabled",
        ])
        self._set_related_initial("exit", EmployeeExit, [
            "resignation_date",
            "last_working_date",
            "exit_reason",
            "exit_notes",
        ])

        self.initial.setdefault("attendance_required", True)
        self.initial.setdefault("login_enabled", True)

    def _apply_required_rules(self) -> None:
        if "employee_id" in self.fields:
            self.fields["employee_id"].required = True
        if "username" in self.fields:
            self.fields["username"].required = True
        if not self.active_tab or self.active_tab == "employment":
            for field in ["organization", "branch", "department", "designation"]:
                if field in self.fields:
                    self.fields[field].required = True

    def _set_related_initial(self, attr_name, model_cls, field_names):
        try:
            related = getattr(self.instance, attr_name)
        except model_cls.DoesNotExist:
            related = None
        if not related:
            return
        for field in field_names:
            self.initial.setdefault(field, getattr(related, field, None))

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise ValidationError("Username is required.")
        existing = User.objects.filter(username=username)
        if self.instance.pk:
            user = getattr(self.instance, "user", None)
            if user:
                existing = existing.exclude(pk=user.pk)
        if existing.exists():
            raise ValidationError("This username is already in use.")
        return username

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk and (self.active_tab and self.active_tab != "basic"):
            raise ValidationError("Create the employee from the Basic tab first.")
        if (not self.instance.pk or (self.active_tab in (None, "basic"))) and not cleaned.get("password"):
            self.add_error("password", "Password is required for new users.")
        return cleaned

    def save(self, commit=True):
        employee = super().save(commit=False)
        if self.active_tab in (None, "basic"):
            username = self.cleaned_data.get("username")
            email = self.cleaned_data.get("email") or ""
            first_name = self.cleaned_data.get("first_name") or ""
            last_name = self.cleaned_data.get("last_name") or ""
            password = self.cleaned_data.get("password")

            user = getattr(employee, "user", None)
            if user:
                user.username = username
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                if password:
                    user.set_password(password)
                if commit:
                    user.save()
            else:
                if password:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )
                else:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                    )
                employee.user = user

        if commit:
            employee.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
            self._save_related_models(employee)
        return employee

    def _save_related_models(self, employee: Employee) -> None:
        if self.active_tab in (None, "basic"):
            profile, _ = EmployeeProfile.objects.get_or_create(employee=employee)
            profile.middle_name = self.cleaned_data.get("middle_name") or ""
            profile.gender = self.cleaned_data.get("gender") or ""
            profile.date_of_birth = self.cleaned_data.get("date_of_birth")
            profile.nationality = self.cleaned_data.get("nationality")
            profile.marital_status = self.cleaned_data.get("marital_status") or ""
            profile.blood_group = self.cleaned_data.get("blood_group") or ""
            if self.cleaned_data.get("profile_photo"):
                profile.profile_photo = self.cleaned_data.get("profile_photo")
            profile.save()

        if self.active_tab in (None, "contact"):
            contact, _ = EmployeeContact.objects.get_or_create(employee=employee)
            contact.phone = self.cleaned_data.get("phone") or ""
            contact.alternate_phone = self.cleaned_data.get("alternate_phone") or ""
            contact.save()

        if self.active_tab in (None, "address"):
            address, _ = EmployeeAddress.objects.get_or_create(employee=employee)
            address.address = self.cleaned_data.get("address") or ""
            address.permanent_address = self.cleaned_data.get("permanent_address") or ""
            address.city = self.cleaned_data.get("city") or ""
            address.state = self.cleaned_data.get("state")
            address.country = self.cleaned_data.get("country")
            address.zip_code = self.cleaned_data.get("zip_code") or ""
            address.save()

        if self.active_tab in (None, "payroll"):
            payroll, _ = EmployeePayroll.objects.get_or_create(employee=employee)
            payroll.salary_type = self.cleaned_data.get("salary_type") or ""
            payroll.basic_salary = self.cleaned_data.get("basic_salary")
            payroll.allowance = self.cleaned_data.get("allowance")
            payroll.overtime_rate = self.cleaned_data.get("overtime_rate")
            payroll.tax_number = self.cleaned_data.get("tax_number") or ""
            payroll.save()

        if self.active_tab in (None, "bank"):
            bank, _ = EmployeeBank.objects.get_or_create(employee=employee)
            bank.bank_name = self.cleaned_data.get("bank_name") or ""
            bank.bank_account_number = self.cleaned_data.get("bank_account_number") or ""
            bank.bank_branch = self.cleaned_data.get("bank_branch") or ""
            bank.payment_method = self.cleaned_data.get("payment_method") or ""
            bank.save()

        if self.active_tab in (None, "legal"):
            legal, _ = EmployeeLegal.objects.get_or_create(employee=employee)
            legal.citizenship_no = self.cleaned_data.get("citizenship_no") or ""
            legal.passport_no = self.cleaned_data.get("passport_no") or ""
            legal.pan_no = self.cleaned_data.get("pan_no") or ""
            legal.social_security_no = self.cleaned_data.get("social_security_no") or ""
            legal.insurance_no = self.cleaned_data.get("insurance_no") or ""
            legal.save()

        if self.active_tab in (None, "work"):
            work, _ = EmployeeWork.objects.get_or_create(employee=employee)
            work.job_description = self.cleaned_data.get("job_description") or ""
            work.work_location = self.cleaned_data.get("work_location") or ""
            work.work_email = self.cleaned_data.get("work_email") or ""
            if self.cleaned_data.get("joining_letter"):
                work.joining_letter = self.cleaned_data.get("joining_letter")
            if self.cleaned_data.get("contract_file"):
                work.contract_file = self.cleaned_data.get("contract_file")
            work.save()

        if self.active_tab in (None, "attendance"):
            attendance, _ = EmployeeAttendance.objects.get_or_create(employee=employee)
            attendance.attendance_required = bool(self.cleaned_data.get("attendance_required"))
            attendance.leave_group = self.cleaned_data.get("leave_group") or ""
            attendance.weekly_off = self.cleaned_data.get("weekly_off") or ""
            attendance.save()

        if self.active_tab in (None, "emergency"):
            emergency, _ = EmployeeEmergency.objects.get_or_create(employee=employee)
            emergency.emergency_contact_name = self.cleaned_data.get("emergency_contact_name") or ""
            emergency.relationship = self.cleaned_data.get("relationship") or ""
            emergency.emergency_phone = self.cleaned_data.get("emergency_phone") or ""
            emergency.emergency_address = self.cleaned_data.get("emergency_address") or ""
            emergency.save()

        if self.active_tab in (None, "access"):
            access, _ = EmployeeAccess.objects.get_or_create(employee=employee)
            access.role = self.cleaned_data.get("role") or ""
            access.permission_group = self.cleaned_data.get("permission_group") or ""
            access.login_enabled = bool(self.cleaned_data.get("login_enabled"))
            access.save()

        if self.active_tab in (None, "exit"):
            exit_info, _ = EmployeeExit.objects.get_or_create(employee=employee)
            exit_info.resignation_date = self.cleaned_data.get("resignation_date")
            exit_info.last_working_date = self.cleaned_data.get("last_working_date")
            exit_info.exit_reason = self.cleaned_data.get("exit_reason") or ""
            exit_info.exit_notes = self.cleaned_data.get("exit_notes") or ""
            exit_info.save()

from __future__ import annotations

import re
from typing import Dict, List

from core.config import EntityConfig
from core.registry import register_entity

from Apps.hr.datatables.employee_data_table import (
    EMPLOYEE_COLUMNS,
    EmployeeDataTableView,
)
from Apps.hr.forms import EmployeeForm
from Apps.hr.models import (
    Employee,
    EmployeeBank,
    EmployeeDocument,
    EmployeePayroll,
    EmployeeProfile,
    EmployeeShift,
    EmployeeWork,
)


DOCUMENT_SECTION = {
    "title": "Documents",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "doc_type", "label": "Type", "type": "text"},
        {"name": "doc_number", "label": "Number", "type": "text"},
        {"name": "file", "label": "File", "type": "file"},
        {"name": "issue_date", "label": "Issue Date", "type": "date"},
        {"name": "expiry_date", "label": "Expiry Date", "type": "date"},
        {"name": "remarks", "label": "Remarks", "type": "text"},
    ],
}

SHIFT_HISTORY_SECTION = {
    "title": "Shift History",
    "layout": "table",
    "allow_add": False,
    "allow_remove": False,
    "fields": [
        {"name": "shift_name", "label": "Shift", "type": "text", "readonly": True},
        {"name": "rotation_status", "label": "Status", "type": "text", "readonly": True},
        {"name": "effective_from_display", "label": "Effective From", "type": "text", "readonly": True},
        {"name": "effective_to_display", "label": "Effective To", "type": "text", "readonly": True},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "readonly": True},
    ],
}


def _parse_dynamic_section(request, section_name: str) -> List[Dict[str, object]]:
    pattern = re.compile(rf"^{re.escape(section_name)}\[(\d+)\]\[(.+)\]$")
    rows: Dict[int, Dict[str, object]] = {}

    for key, value in request.POST.items():
        match = pattern.match(key)
        if not match:
            continue
        index = int(match.group(1))
        field = match.group(2)
        rows.setdefault(index, {})[field] = value

    for key, value in request.FILES.items():
        match = pattern.match(key)
        if not match:
            continue
        index = int(match.group(1))
        field = match.group(2)
        rows.setdefault(index, {})[field] = value

    return [rows[idx] for idx in sorted(rows.keys())]


def _save_employee_documents(request, employee: Employee) -> None:
    active_tab = (request.POST.get("_active_tab") or "").strip()
    if active_tab and active_tab != "documents":
        return

    rows = _parse_dynamic_section(request, "documents")
    existing = {doc.id: doc for doc in EmployeeDocument.objects.filter(employee=employee)}
    keep_ids = []

    for row in rows:
        doc_id = row.get("id")
        doc = None
        if doc_id and str(doc_id).isdigit():
            doc = existing.get(int(doc_id))

        if not doc:
            doc = EmployeeDocument(employee=employee)

        has_data = False
        for field in ["doc_type", "doc_number", "issue_date", "expiry_date", "remarks"]:
            value = row.get(field)
            if value:
                has_data = True
            setattr(doc, field, value or "")

        file_value = row.get("file")
        if file_value:
            has_data = True
            doc.file = file_value

        if has_data:
            doc.save()
            keep_ids.append(doc.id)

    if keep_ids:
        EmployeeDocument.objects.filter(employee=employee).exclude(id__in=keep_ids).delete()
    else:
        EmployeeDocument.objects.filter(employee=employee).delete()


def _load_employee_documents(employee: Employee) -> Dict[str, List[Dict[str, object]]]:
    rows = []
    for doc in EmployeeDocument.objects.filter(employee=employee):
        rows.append(
            {
                "id": doc.id,
                "doc_type": doc.doc_type,
                "doc_number": doc.doc_number,
                "issue_date": doc.issue_date.strftime("%Y-%m-%d") if doc.issue_date else "",
                "expiry_date": doc.expiry_date.strftime("%Y-%m-%d") if doc.expiry_date else "",
                "remarks": doc.remarks,
            }
        )
    return {"documents": rows}


def _rotation_status(rotation: EmployeeShift) -> str:
    from django.utils import timezone

    now = timezone.localtime()
    if rotation.effective_from and rotation.effective_from > now:
        return "Upcoming"
    if rotation.effective_to and rotation.effective_to < now:
        return "Expired"
    return "Current"


def _load_employee_shift_history(employee: Employee) -> Dict[str, List[Dict[str, object]]]:
    rows = []
    rotations = (
        EmployeeShift.objects.filter(employee=employee)
        .select_related("shift")
        .order_by("-effective_from", "-created_at", "-id")
    )
    for rotation in rotations:
        rows.append(
            {
                "id": rotation.id,
                "shift_name": rotation.shift.name or rotation.shift.code or str(rotation.shift),
                "rotation_status": _rotation_status(rotation),
                "effective_from_display": rotation.effective_from.strftime("%Y-%m-%d %H:%M") if rotation.effective_from else "",
                "effective_to_display": rotation.effective_to.strftime("%Y-%m-%d %H:%M") if rotation.effective_to else "",
                "remarks": rotation.remarks,
            }
        )
    return {"shift_history": rows}


def _load_employee_dynamic_sections(employee: Employee) -> Dict[str, List[Dict[str, object]]]:
    data = {}
    data.update(_load_employee_documents(employee))
    data.update(_load_employee_shift_history(employee))
    return data


register_entity(
    EntityConfig(
        name="employee",
        url_path="employees",
        verbose_name="Employee",
        model=Employee,
        form_class=EmployeeForm,
        datatable_view=EmployeeDataTableView,
        fields=[],
        tabs=[
            {
                "key": "basic",
                "label": "Basic",
                "fields": [
                    {
                        "name": "employee_id",
                        "label": "Employee ID",
                        "type": "text",
                        "required": True,
                        "col": 4,
                        "placeholder": "EMP-001",
                    },
                    {
                        "name": "employee_code",
                        "label": "Employee Code",
                        "type": "text",
                        "required": False,
                        "col": 4,
                        "placeholder": "EMP",
                    },
                    {
                        "name": "username",
                        "label": "Username",
                        "type": "text",
                        "required": True,
                        "col": 4,
                        "placeholder": "sita.sharma",
                    },
                    {
                        "name": "email",
                        "label": "Email",
                        "type": "email",
                        "required": False,
                        "col": 4,
                        "placeholder": "user@example.com",
                    },
                    {
                        "name": "first_name",
                        "label": "First Name",
                        "type": "text",
                        "required": False,
                        "col": 4,
                        "placeholder": "Sita",
                    },
                    {
                        "name": "middle_name",
                        "label": "Middle Name",
                        "type": "text",
                        "required": False,
                        "col": 4,
                        "placeholder": "Kumari",
                    },
                    {
                        "name": "last_name",
                        "label": "Last Name",
                        "type": "text",
                        "required": False,
                        "col": 4,
                        "placeholder": "Sharma",
                    },
                    {
                        "name": "password",
                        "label": "Password",
                        "type": "password",
                        "required": False,
                        "col": 4,
                        "placeholder": "Set password",
                    },
                    {
                        "name": "gender",
                        "label": "Gender",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": EmployeeProfile.GENDER_CHOICES,
                    },
                    {
                        "name": "date_of_birth",
                        "label": "Date of Birth",
                        "type": "date",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "nationality",
                        "label": "Nationality",
                        "type": "select",
                        "required": False,
                        "col": 4,
                        "url_name": "country_select",
                    },
                    {
                        "name": "marital_status",
                        "label": "Marital Status",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": EmployeeProfile.MARITAL_STATUS_CHOICES,
                    },
                    {
                        "name": "blood_group",
                        "label": "Blood Group",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": EmployeeProfile.BLOOD_GROUP_CHOICES,
                    },
                    {
                        "name": "profile_photo",
                        "label": "Profile Photo",
                        "type": "file",
                        "required": False,
                        "col": 4,
                    },
                ],
            },
            {
                "key": "contact",
                "label": "Contact",
                "requires_id": True,
                "fields": [
                    {
                        "name": "phone",
                        "label": "Phone",
                        "type": "text",
                        "required": False,
                        "col": 4,
                        "placeholder": "+977-98XXXXXXXX",
                    },
                    {
                        "name": "alternate_phone",
                        "label": "Alternate Phone",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                ],
            },
            {
                "key": "address",
                "label": "Address",
                "requires_id": True,
                "fields": [
                    {
                        "name": "address",
                        "label": "Current Address",
                        "type": "textarea",
                        "required": False,
                        "col": 6,
                    },
                    {
                        "name": "permanent_address",
                        "label": "Permanent Address",
                        "type": "textarea",
                        "required": False,
                        "col": 6,
                    },
                    {
                        "name": "city",
                        "label": "City",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "state",
                        "label": "State",
                        "type": "select",
                        "required": False,
                        "col": 4,
                        "url_name": "state_select",
                    },
                    {
                        "name": "country",
                        "label": "Country",
                        "type": "select",
                        "required": False,
                        "col": 4,
                        "url_name": "country_select",
                    },
                    {
                        "name": "zip_code",
                        "label": "Zip Code",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                ],
            },
            {
                "key": "employment",
                "label": "Employment",
                "requires_id": True,
                "fields": [
                    {
                        "name": "organization",
                        "label": "Organization",
                        "type": "select",
                        "required": True,
                        "col": 6,
                        "url_name": "organization_select",
                    },
                    {
                        "name": "branch",
                        "label": "Branch",
                        "type": "select",
                        "required": True,
                        "col": 6,
                        "url_name": "branch_select",
                    },
                    {
                        "name": "department",
                        "label": "Department",
                        "type": "select",
                        "required": True,
                        "col": 6,
                        "url_name": "department_select",
                    },
                    {
                        "name": "designation",
                        "label": "Designation",
                        "type": "select",
                        "required": True,
                        "col": 6,
                        "url_name": "designation_select",
                    },
                    {
                        "name": "reporting_manager",
                        "label": "Reporting Manager",
                        "type": "select",
                        "required": False,
                        "col": 6,
                        "url_name": "employee_select",
                    },
                    {
                        "name": "join_date",
                        "label": "Join Date",
                        "type": "date",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "employee_type",
                        "label": "Employee Type",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": Employee.EMPLOYEE_TYPE_CHOICES,
                    },
                    {
                        "name": "employment_status",
                        "label": "Employment Status",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": Employee.EMPLOYMENT_STATUS_CHOICES,
                    },
                    {
                        "name": "shift",
                        "label": "Shift",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "probation_period",
                        "label": "Probation Period (Months)",
                        "type": "number",
                        "required": False,
                        "col": 4,
                        "attributes": {"min": "0"},
                    },
                    {
                        "name": "is_active",
                        "label": "Active",
                        "type": "checkbox",
                        "required": False,
                        "col": 4,
                        "default": True,
                    },
                ],
            },
            {
                "key": "payroll",
                "label": "Payroll",
                "requires_id": True,
                "fields": [
                    {
                        "name": "salary_type",
                        "label": "Salary Type",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": EmployeePayroll.SALARY_TYPE_CHOICES,
                    },
                    {
                        "name": "basic_salary",
                        "label": "Basic Salary",
                        "type": "number",
                        "required": False,
                        "col": 4,
                        "attributes": {"min": "0", "step": "0.01"},
                    },
                    {
                        "name": "allowance",
                        "label": "Allowance",
                        "type": "number",
                        "required": False,
                        "col": 4,
                        "attributes": {"min": "0", "step": "0.01"},
                    },
                    {
                        "name": "overtime_rate",
                        "label": "Overtime Rate",
                        "type": "number",
                        "required": False,
                        "col": 4,
                        "attributes": {"min": "0", "step": "0.01"},
                    },
                    {
                        "name": "tax_number",
                        "label": "Tax Number",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                ],
            },
            {
                "key": "bank",
                "label": "Bank",
                "requires_id": True,
                "fields": [
                    {
                        "name": "bank_name",
                        "label": "Bank Name",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "bank_account_number",
                        "label": "Bank Account Number",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "bank_branch",
                        "label": "Bank Branch",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "payment_method",
                        "label": "Payment Method",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": EmployeeBank.PAYMENT_METHOD_CHOICES,
                    },
                ],
            },
            {
                "key": "legal",
                "label": "Legal",
                "requires_id": True,
                "fields": [
                    {
                        "name": "citizenship_no",
                        "label": "Citizenship No",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "passport_no",
                        "label": "Passport No",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "pan_no",
                        "label": "PAN No",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "social_security_no",
                        "label": "SSF No",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "insurance_no",
                        "label": "Insurance No",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                ],
            },
            {
                "key": "work",
                "label": "Work",
                "requires_id": True,
                "fields": [
                    {
                        "name": "job_description",
                        "label": "Job Description",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                    },
                    {
                        "name": "work_location",
                        "label": "Work Location",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": EmployeeWork.WORK_LOCATION_CHOICES,
                    },
                    {
                        "name": "work_email",
                        "label": "Work Email",
                        "type": "email",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "joining_letter",
                        "label": "Joining Letter",
                        "type": "file",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "contract_file",
                        "label": "Contract File",
                        "type": "file",
                        "required": False,
                        "col": 4,
                    },
                ],
            },
            {
                "key": "attendance",
                "label": "Attendance",
                "requires_id": True,
                "fields": [
                    {
                        "name": "attendance_required",
                        "label": "Attendance Required",
                        "type": "checkbox",
                        "required": False,
                        "col": 4,
                        "default": True,
                    },
                    {
                        "name": "leave_group",
                        "label": "Leave Group",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "weekly_off",
                        "label": "Weekly Off",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                ],
            },
            {
                "key": "emergency",
                "label": "Emergency",
                "requires_id": True,
                "fields": [
                    {
                        "name": "emergency_contact_name",
                        "label": "Emergency Contact Name",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "relationship",
                        "label": "Relationship",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "emergency_phone",
                        "label": "Emergency Phone",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "emergency_address",
                        "label": "Emergency Address",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                    },
                ],
            },
            {
                "key": "access",
                "label": "Access",
                "requires_id": True,
                "fields": [
                    {
                        "name": "login_enabled",
                        "label": "Login Enabled",
                        "type": "checkbox",
                        "required": False,
                        "col": 4,
                        "default": True,
                    },
                    {
                        "name": "role",
                        "label": "Role",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "permission_group",
                        "label": "Permission Group",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                ],
            },
            {
                "key": "exit",
                "label": "Exit",
                "requires_id": True,
                "fields": [
                    {
                        "name": "resignation_date",
                        "label": "Resignation Date",
                        "type": "date",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "last_working_date",
                        "label": "Last Working Date",
                        "type": "date",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "exit_reason",
                        "label": "Exit Reason",
                        "type": "text",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "exit_notes",
                        "label": "Exit Notes",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                    },
                    {
                        "name": "remarks",
                        "label": "Remarks",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                    },
                ],
            },
            {
                "key": "documents",
                "label": "Documents",
                "requires_id": True,
                "fields": [],
                "sections": ["documents"],
            },
            {
                "key": "shift_history",
                "label": "Shift History",
                "fields": [],
                "sections": ["shift_history"],
                "requires_id": True,
            },
        ],
        dynamic_sections={
            "documents": DOCUMENT_SECTION,
            "shift_history": SHIFT_HISTORY_SECTION,
        },
        dynamic_sections_loader=_load_employee_dynamic_sections,
        dynamic_sections_saver=_save_employee_documents,
        datatable_columns=[
            (
                {
                    "name": key,
                    "title": "Active",
                    "render": "function(data){return data ? 'Yes' : 'No';}",
                }
                if key == "is_active"
                else {
                    "name": key,
                    "title": {
                        "employee_id": "Employee ID",
                        "employment_status": "Status",
                    }.get(key, key.replace("_", " ").title()),
                }
            )
            for key, _accessor in EMPLOYEE_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "is_active": True,
            "attendance_required": True,
            "login_enabled": True,
            "employment_status": "active",
        },
    )
)

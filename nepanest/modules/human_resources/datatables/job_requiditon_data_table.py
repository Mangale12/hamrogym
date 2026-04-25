from core.datatables.views import BaseDataTableView
from nepanest.common.helpers.helper import encode_date_for_display
from nepanest.modules.recruitment.models import JobRequisition


JOB_REQUISITION_COLUMNS = [
    ("id", "id"),
    ("requisition_code", "requisition_code"),
    ("job_title", "job_title"),
    ("batch", "batch.name"),
    ("branch", "branch.name"),
    ("department", "department.name"),
    ("designation", "designation.name"),
    ("employment_type", "employment_type.name"),
    ("requested_by", lambda obj: obj.requested_by.get_full_name() or obj.requested_by.username if obj.requested_by else ""),
    ("priority", "priority"),
    ("status", "status"),
    ("expected_joining_date", lambda obj, request: encode_date_for_display(obj.expected_joining_date, request)),
]


class JobRequisitionDataTableView(BaseDataTableView):
    model = JobRequisition
    columns = JOB_REQUISITION_COLUMNS
    searchable_columns = [
        "requisition_code",
        "job_title",
        "department__name",
        "batch__name",
        "branch__name",
        "status",
        "designation__name",
        "employment_type__name",
        "requested_by__username",
        "requested_by__first_name",
        "requested_by__last_name",
        "priority",
    ]
    orderable_columns = [
        "requisition_code",
        "job_title",
        "batch__name",
        "branch__name",
        "department__name",
        "designation__name",
        "employment_type__name",
        "requested_by__username",
        "priority",
        "status",
        "expected_joining_date",
    ]

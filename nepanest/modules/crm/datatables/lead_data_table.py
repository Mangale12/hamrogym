from core.datatables.views import BaseDataTableView
from ..models import Lead


LEAD_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("email", "email"),
    ("phone", "phone"),
    ("company_name", "company_name"),
    ("lead_source__name", "lead_source.name"),
    ("lead_status__name", "lead_status.name"),
    ("assigned_to__username", "assigned_to.username"),
    ("service__name", "service.name"),
    ("budget", "budget"),
    ("last_contacted", "last_contacted"),
    ("next_followup", "next_followup"),
    # TODO: add columns
]


class LeadDataTableView(BaseDataTableView):
    model = Lead
    columns = LEAD_COLUMNS
    searchable_columns = [
        "name",
        "email",
        "phone",
        "company_name",
        "lead_source__name",
        "lead_status__name",
        "assigned_to__username",
        "service__name",
        # TODO: add searchable fields
    ]
    orderable_columns = [
        "name",
        "email",
        "phone",
        "company_name",
        "lead_source__name",
        "lead_status__name",
        "assigned_to__username",
        "service__name",
        "budget",
        "last_contacted",
        "next_followup",
    ]

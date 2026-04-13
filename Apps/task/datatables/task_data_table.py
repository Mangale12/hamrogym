from core.datatables.views import BaseDataTableView
from ..models import Task


TASK_COLUMNS = [
    ("id", "id"),
    ("code", "code"),
    ("title", "title"),
    ("project", "project.name"),
    ("epic", "epic.name"),
    ("module", "module.name"),
    ("task_type", "task_type.name"),
    ("assignee", lambda obj: obj.assignee.get_full_name() or obj.assignee.username if obj.assignee else ""),
    ("team", "team.name"),
    ("status", "status.name"),
    ("priority", lambda obj: obj.get_priority_display()),
    ("severity", lambda obj: obj.get_severity_display()),
    ("progress", "progress"),
    ("due_date", "due_date"),
    ("is_billable", lambda obj: "Yes" if obj.is_billable else "No"),
    ("billable_to", lambda obj: obj.get_billable_to_display() if obj.is_billable else ""),
    ("currency", lambda obj: getattr(obj.currency, "code", "")),
    ("billing_company_name", "billing_company_name"),
    ("billing_amount", lambda obj: obj.billing_amount if obj.is_billable else ""),
    ("billing_status", lambda obj: obj.get_billing_status_display()),
    ("labels", lambda obj: ", ".join(label.name for label in obj.labels.all())),
    ("is_blocked", lambda obj: "Yes" if obj.is_blocked else "No"),
    ("approval_status", lambda obj: obj.get_approval_status_display()),
    ("is_active", "is_active"),
]


class TaskDataTableView(BaseDataTableView):
    model = Task
    columns = TASK_COLUMNS
    searchable_columns = [
        "code",
        "title",
        "description",
        "project__name",
        "epic__name",
        "module__name",
        "task_type__name",
        "assignee__username",
        "assignee__first_name",
        "assignee__last_name",
        "team__name",
        "status__name",
        "priority",
        "severity",
        "labels__name",
        "billable_to",
        "currency__code",
        "billing_company_name",
        "billing_status",
        "invoice_reference",
        "remarks",
    ]
    orderable_columns = [
        "code",
        "title",
        "project__name",
        "epic__name",
        "module__name",
        "task_type__name",
        "assignee__username",
        "team__name",
        "status__name",
        "priority",
        "severity",
        "progress",
        "due_date",
        "is_billable",
        "billable_to",
        "currency__code",
        "billing_company_name",
        "billing_amount",
        "billing_status",
        "labels__name",
        "is_blocked",
        "approval_status",
        "is_active",
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("project", "epic", "module", "task_type", "assignee", "team", "status", "currency")
            .prefetch_related("labels")
        )

    def filter_queryset(self, queryset, search_value):
        queryset = super().filter_queryset(queryset, search_value)
        return queryset.distinct() if search_value else queryset

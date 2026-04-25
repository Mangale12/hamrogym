from core.datatables.views import BaseDataTableView
from nepanest.modules.policies.models import Policy


POLICY_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("code", "code"),
    ("module", "module"),
    ("trigger_event", "trigger_event"),
    ("priority", "priority"),
    ("is_active", "is_active"),
    ("effective_from", "effective_from"),
    ("effective_to", "effective_to"),
]


class PolicyDataTableView(BaseDataTableView):
    model = Policy
    columns = POLICY_COLUMNS
    searchable_columns = [
        "name",
        "code",
        "module",
        "trigger_event",
        "description",
    ]
    orderable_columns = [
        "name",
        "code",
        "module",
        "trigger_event",
        "priority",
        "is_active",
        "effective_from",
        "effective_to",
    ]

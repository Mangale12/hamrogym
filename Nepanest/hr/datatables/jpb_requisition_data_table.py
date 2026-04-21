from core.datatables.views import BaseDataTableView
from ..models import JobRequisition


JPB_REQUISITION_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class JobRequisitionDataTableView(BaseDataTableView):
    model = JobRequisition
    columns = JPB_REQUISITION_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]

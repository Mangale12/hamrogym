from core.datatables.views import BaseDataTableView
from ..models import JobRequisition


JOB_REQUIDITON_COLUMNS = [
    ("id", "id"),
    # TODO: add columns
]


class JobRequisitionDataTableView(BaseDataTableView):
    model = JobRequisition
    columns = JOB_REQUIDITON_COLUMNS
    searchable_columns = [
        # TODO: add searchable fields
    ]
    orderable_columns = [
        # TODO: add orderable fields
    ]

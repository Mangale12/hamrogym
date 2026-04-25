from core.datatables.views import BaseDataTableView
from nepanest.modules.recruitment.models import JobPosition


JOB_POSITION_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("department", "department.name"),
    ("designation", "designation.name"),
    ("job_category", "job_category.name"),
    ("vacancies", "vacancies"),
    ("employeement_type", "employeement_type.name"),
    ("salary_min", "salary_min"),
    ("salary_max", "salary_max"),
    ("is_active", "is_active"),
    ("remarks", "remarks"),
]


class JobPositionDataTableView(BaseDataTableView):
    model = JobPosition
    columns = JOB_POSITION_COLUMNS
    searchable_columns = [
        "name",
        "department__name",
        "designation__name",
        "job_category__name",
        "employeement_type__name",
        "is_active",
        "remarks",
    ]
    orderable_columns = [
        "id",
        "name",
        "department__name",
        "designation__name",
        "job_category__name",
        "vacancies",
        "employeement_type__name",
        "salary_min",
        "salary_max",
        "is_active",
        "remarks",
    ]

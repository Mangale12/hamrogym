from core.datatables.views import BaseDataTableView
from nepanest.foundation.geography import Country


class CountryDataTableView(BaseDataTableView):
    model = Country
    columns = [
        ("name", "name"),
        ("iso2", "iso2"),
        ("iso3", "iso3"),
        ("phone_code", "phone_code"),
        ("is_active", "is_active"),
        ("id", "id"),
    ]
    searchable_columns = ["name", "iso2", "iso3", "phone_code"]
    orderable_columns = ["name", "iso2", "iso3", "phone_code", "is_active", "id"]

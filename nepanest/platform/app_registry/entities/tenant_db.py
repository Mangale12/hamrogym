from core.config import EntityConfig
from core.registry import register_entity

from ..datatables.tenant_db_data_table import TENANT_DB_COLUMNS, TenantDBDataTableView
from ..forms.tenant_db_form import TenantDBForm
from ..models import TenantDB


register_entity(
    EntityConfig(
        name="tenant_db",
        url_path="tenant-dbs",
        verbose_name="Tenant DB",
        model=TenantDB,
        form_class=TenantDBForm,
        datatable_view=TenantDBDataTableView,
        fields=[
            {
                "name": "client",
                "label": "Client",
                "type": "select",
                "required": True,
                "col": 6,
                "url_name": "client_select",
            },
            {"name": "db_name", "label": "DB Name", "type": "text", "required": True, "col": 6},
            {"name": "db_user", "label": "DB User", "type": "text", "required": True, "col": 6},
            {"name": "db_password", "label": "DB Password", "type": "password", "required": True, "col": 6},
            {"name": "db_host", "label": "DB Host", "type": "text", "required": True, "col": 6},
            {"name": "db_port", "label": "DB Port", "type": "text", "required": True, "col": 6},
            {
                "name": "status",
                "label": "Status",
                "type": "static_select",
                "required": True,
                "col": 6,
                "options": TenantDB.Status.choices,
            },
        ],
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in TENANT_DB_COLUMNS
            if key != "id"
        ],
        reset_defaults={
            "db_host": "127.0.0.1",
            "db_port": "3306",
            "status": TenantDB.Status.TRIAL,
        },
        select_search_fields=["db_name", "db_user", "client__business_name", "client__client_code", "status"],
        select_label_func=lambda obj: f"{obj.client} - {obj.db_name}",
    )
)

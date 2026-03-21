from django.contrib.auth import get_user_model

from core.config import EntityConfig
from core.datatables.user import UserDataTableView
from core.forms.user_form import UserForm
from core.registry import register_entity


User = get_user_model()


register_entity(
    EntityConfig(
        name="user",
        url_path="users",
        verbose_name="User",
        model=User,
        form_class=UserForm,
        datatable_view=UserDataTableView,
        fields=[
            {
                "name": "username",
                "label": "Username",
                "type": "text",
                "required": True,
                "col": 4,
                "placeholder": "jdoe",
            },
            {
                "name": "first_name",
                "label": "First Name",
                "type": "text",
                "required": False,
                "col": 4,
                "placeholder": "John",
            },
            {
                "name": "last_name",
                "label": "Last Name",
                "type": "text",
                "required": False,
                "col": 4,
                "placeholder": "Doe",
            },
            {
                "name": "email",
                "label": "Email",
                "type": "email",
                "required": False,
                "col": 6,
                "placeholder": "john@example.com",
            },
            {
                "name": "password",
                "label": "Password",
                "type": "password",
                "required": False,
                "col": 6,
                "placeholder": "Enter a secure password",
                "help": "Required when creating a user. Leave blank on edit to keep the current password.",
            },
            {
                "name": "is_active",
                "label": "Active User",
                "type": "checkbox",
                "required": False,
                "col": 4,
                "default": True,
            },
            {
                "name": "is_staff",
                "label": "Staff Access",
                "type": "checkbox",
                "required": False,
                "col": 4,
                "default": False,
            },
            {
                "name": "is_superuser",
                "label": "Administrator",
                "type": "checkbox",
                "required": False,
                "col": 4,
                "default": False,
            },
        ],
        datatable_columns=[
            {"name": "username", "title": "Username"},
            {
                "name": "full_name",
                "title": "Full Name",
                "render": "function(data){return data || '-';}",
            },
            {
                "name": "email",
                "title": "Email",
                "render": "function(data){return data || '-';}",
            },
            {
                "name": "is_active",
                "title": "Active",
                "render": "function(data){return data ? 'Yes' : 'No';}",
            },
            {
                "name": "is_staff",
                "title": "Staff",
                "render": "function(data){return data ? 'Yes' : 'No';}",
            },
            {"name": "date_joined", "title": "Joined On"},
        ],
        reset_defaults={"is_active": True, "is_staff": False, "is_superuser": False},
    )
)

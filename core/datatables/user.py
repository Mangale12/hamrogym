from django.contrib.auth import get_user_model

from core.datatables.views import BaseDataTableView
from core.helpers.helper import encode_date_for_display


User = get_user_model()


class UserDataTableView(BaseDataTableView):
    model = User
    columns = [
        ("id", "id"),
        ("username", "username"),
        ("full_name", lambda obj: obj.get_full_name().strip()),
        ("email", "email"),
        ("is_active", "is_active"),
        ("is_staff", "is_staff"),
        (
            "date_joined",
            lambda obj, request: (
                f"{encode_date_for_display(obj.date_joined.date(), request)} {obj.date_joined.strftime('%H:%M')}"
            )
            if obj.date_joined
            else "",
        ),
    ]
    searchable_columns = ["username", "email", "first_name", "last_name"]
    orderable_columns = ["username", "first_name", "email", "is_active", "is_staff", "date_joined"]

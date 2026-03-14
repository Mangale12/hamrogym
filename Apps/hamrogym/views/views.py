from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render

from core.datatables import DataTableServer


@login_required
def dashboard(request):
    return render(request, "index.html")


@login_required
def users_datatable(request):
    queryset = User.objects.all()
    datatable = DataTableServer(
        request=request,
        queryset=queryset,
        columns=["id", "username", "email", "is_active", "is_staff", "date_joined"],
        search_fields=["username", "email", "first_name", "last_name"],
    )

    def row_builder(user):
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": "Yes" if user.is_active else "No",
            "is_staff": "Yes" if user.is_staff else "No",
            "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M"),
        }

    return JsonResponse(datatable.get_result(row_builder=row_builder))

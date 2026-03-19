from django.urls import path

from .views.user_select import user_select


urlpatterns = [
    path("select/users/", user_select, name="user_select"),
]

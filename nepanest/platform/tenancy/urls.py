from django.urls import path

from .views import TenantLoginView


urlpatterns = [
    path("login/", TenantLoginView.as_view(), name="login"),
]

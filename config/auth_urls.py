from django.urls import include, path

from nepanest.platform.tenancy.views import TenantLoginView


urlpatterns = [
    path("login/", TenantLoginView.as_view(), name="login"),
    path("", include("django.contrib.auth.urls")),
]

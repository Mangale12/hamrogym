from django.urls import include, path

from core.views.auth import RememberMeLoginView


urlpatterns = [
    path("login/", RememberMeLoginView.as_view(), name="login"),
    path("", include("django.contrib.auth.urls")),
]

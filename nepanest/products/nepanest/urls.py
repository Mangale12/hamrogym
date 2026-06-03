from django.urls import path
from django.views.generic import RedirectView

from nepanest.products.nepanest.views import views


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="platform_dashboard", permanent=False)),
    path("dashboard/", views.dashboard, name="platform_dashboard"),
]

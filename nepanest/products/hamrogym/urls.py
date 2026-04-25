from django.views.generic import RedirectView
from django.urls import path

from nepanest.products.hamrogym.views import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="dashboard", permanent=False)),
    path("product/hamrogym/dashboard/", views.dashboard, name="dashboard"),
]

from django.urls import path
from django.views.generic import RedirectView

from nepanest.products.hamrogym.views import views

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="dashboard", permanent=False)),
    path("product/hamrogym/dashboard/", views.dashboard, name="dashboard"),
    path(
        "product/hamrogym/members/available-parties/",
        views.member_available_party_select,
        name="member_available_party_select",
    ),
]

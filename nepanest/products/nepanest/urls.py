from django.urls import path

from nepanest.products.nepanest.views import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]


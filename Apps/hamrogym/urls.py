from django.urls import path

from Apps.hamrogym.views import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]

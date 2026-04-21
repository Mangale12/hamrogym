from django.urls import path

from Nepanest.hamrogym.views import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]

from django.urls import path

from Apps.hamrogym.views import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('datatable/users/', views.users_datatable, name='users_datatable'),
]

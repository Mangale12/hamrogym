from django.urls import path

from nepanest.products.hamrogym.views import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]

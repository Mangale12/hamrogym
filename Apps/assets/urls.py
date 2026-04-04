from django.urls import path

from .views import AssetProfileView


urlpatterns = [
    path("asset/<int:pk>/profile/", AssetProfileView.as_view(), name="asset_profile"),
]

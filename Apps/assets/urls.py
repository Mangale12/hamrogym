from django.urls import path

from .views import AssetProfileView, MonthlyDepreciationPostView, MonthlyDepreciationRunView


urlpatterns = [
    path("asset/<int:pk>/profile/", AssetProfileView.as_view(), name="asset_profile"),
    path(
        "asset-depreciation-registers/run-monthly/",
        MonthlyDepreciationRunView.as_view(),
        name="asset_depreciation_register_run_monthly",
    ),
    path(
        "asset-depreciation-registers/post-monthly/",
        MonthlyDepreciationPostView.as_view(),
        name="asset_depreciation_register_post_monthly",
    ),
]

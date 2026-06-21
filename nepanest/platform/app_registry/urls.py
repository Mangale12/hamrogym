from django.urls import path
from django.views.generic import RedirectView

from core.registry import get_entities
from core.views.entities import build_entity_views

from .views import RegistryDashboardView, RegistryLoginView, RegistryLogoutView


app_name = "app_registry"

urlpatterns = [
    path("", RegistryDashboardView.as_view(), name="dashboard"),
    path("dashboard/", RedirectView.as_view(pattern_name="app_registry:dashboard", permanent=False), name="home"),
    path("login/", RegistryLoginView.as_view(), name="login"),
    path("logout/", RegistryLogoutView.as_view(), name="logout"),
]

# Expose entity views for registry namespace for entities belonging to the app_registry app.
for entity in get_entities():
    # Filter entities whose model belongs to the app_registry app label
    try:
        app_label = entity.model._meta.app_label
    except Exception:
        app_label = None
    if app_label != "app_registry":
        continue

    views = build_entity_views(entity)
    url_base = entity.url_base
    name = entity.name

    urlpatterns.extend([
        path(f"{url_base}/", views["list_view"].as_view(), name=f"{name}_list"),
        path(f"{url_base}/create/", views["create_view"].as_view(), name=f"{name}_create"),
        path(f"{url_base}/<int:pk>/update/", views["update_view"].as_view(), name=f"{name}_update"),
        path(f"{url_base}/<int:pk>/detail/", views["detail_view"].as_view(), name=f"{name}_detail"),
        path(f"{url_base}/<int:pk>/delete/", views["delete_view"].as_view(), name=f"{name}_delete"),
        path(f"{url_base}/datatable/", views["datatable_view"].as_view(), name=f"{name}_datatable"),
        path(f"{url_base}/select/", views["select_view"].as_view(), name=f"{name}_select"),
    ])

    for action_name, action_view in views.get("action_views", {}).items():
        urlpatterns.append(path(f"{url_base}/<int:pk>/{action_name}/", action_view.as_view(), name=f"{name}_{action_name}"))

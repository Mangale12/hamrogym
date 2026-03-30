from django.urls import path

from core.registry import get_entities
from core.views.entities import build_entity_views
from core.views.calendar_switch import CalendarSwitchView

urlpatterns = []

urlpatterns.append(
    path("calendar/switch/", CalendarSwitchView.as_view(), name="calendar_switch")
)

for entity in get_entities():
    views = build_entity_views(entity)
    url_base = entity.url_base
    name = entity.name

    urlpatterns.extend(
        [
            path(f"{url_base}/", views["list_view"].as_view(), name=f"{name}_list"),
            path(
                f"{url_base}/create/",
                views["create_view"].as_view(),
                name=f"{name}_create",
            ),
            path(
                f"{url_base}/<int:pk>/update/",
                views["update_view"].as_view(),
                name=f"{name}_update",
            ),
            path(
                f"{url_base}/<int:pk>/detail/",
                views["detail_view"].as_view(),
                name=f"{name}_detail",
            ),
            path(
                f"{url_base}/<int:pk>/delete/",
                views["delete_view"].as_view(),
                name=f"{name}_delete",
            ),
            path(
                f"{url_base}/datatable/",
                views["datatable_view"].as_view(),
                name=f"{name}_datatable",
            ),
            path(
                f"{url_base}/select/",
                views["select_view"].as_view(),
                name=f"{name}_select",
            ),
        ]
    )

    for action_name, action_view in views.get("action_views", {}).items():
        urlpatterns.append(
            path(
                f"{url_base}/<int:pk>/{action_name}/",
                action_view.as_view(),
                name=f"{name}_{action_name}",
            )
        )

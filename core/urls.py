from django.urls import path

from core.registry import get_entities
from Nepanest.task.views import (
    ChecklistTemplateItemsView,
    TaskBillingGenerateView,
    TaskBillingStatusUpdateView,
    TaskCommentAddView,
    TaskCommentUpdateView,
    TaskChecklistAddView,
    TaskChecklistUpdateView,
    TaskDetailPageView,
    TaskKanbanStatusUpdateView,
    TaskMemberAddView,
    TaskBoardView,
    TaskTimeLogApprovalView,
    TaskTimeLogAddView,
)
from core.views.entities import build_entity_views
from core.views.calendar_switch import CalendarSwitchView

urlpatterns = []

urlpatterns.append(
    path("calendar/switch/", CalendarSwitchView.as_view(), name="calendar_switch")
)
urlpatterns.append(
    path(
        "tasks/checklist-template-items/",
        ChecklistTemplateItemsView.as_view(),
        name="task_checklist_template_items",
    )
)
urlpatterns.append(
    path("tasks/<int:pk>/view/", TaskDetailPageView.as_view(), name="task_view")
)
urlpatterns.append(path("tasks/board/", TaskBoardView.as_view(), name="task_board"))
urlpatterns.append(
    path("tasks/board/update-status/", TaskKanbanStatusUpdateView.as_view(), name="task_kanban_update_status")
)
urlpatterns.append(
    path("tasks/<int:pk>/checklist/add/", TaskChecklistAddView.as_view(), name="task_checklist_add")
)
urlpatterns.append(
    path(
        "tasks/<int:pk>/checklist/<int:item_id>/update/",
        TaskChecklistUpdateView.as_view(),
        name="task_checklist_update",
    )
)
urlpatterns.append(
    path("tasks/<int:pk>/members/add/", TaskMemberAddView.as_view(), name="task_member_add")
)
urlpatterns.append(
    path("tasks/<int:pk>/comments/add/", TaskCommentAddView.as_view(), name="task_comment_add")
)
urlpatterns.append(
    path(
        "tasks/<int:pk>/comments/<int:comment_id>/update/",
        TaskCommentUpdateView.as_view(),
        name="task_comment_update",
    )
)
urlpatterns.append(
    path("tasks/<int:pk>/timelogs/add/", TaskTimeLogAddView.as_view(), name="task_timelog_add")
)
urlpatterns.append(
    path(
        "tasks/<int:pk>/timelogs/<int:log_id>/approve/",
        TaskTimeLogApprovalView.as_view(),
        name="task_timelog_approve",
    )
)
urlpatterns.append(
    path("tasks/<int:pk>/billings/generate/", TaskBillingGenerateView.as_view(), name="task_billing_generate")
)
urlpatterns.append(
    path(
        "tasks/<int:pk>/billings/<int:billing_id>/status/",
        TaskBillingStatusUpdateView.as_view(),
        name="task_billing_status_update",
    )
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

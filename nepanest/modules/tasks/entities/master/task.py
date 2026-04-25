import re

from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.utils.dynamic_sections import (
    RelatedDynamicSectionConfig,
    build_related_section_loader,
    build_related_section_saver,
)

from ...datatables.task_data_table import TASK_COLUMNS, TaskDataTableView
from ...forms.task_form import TaskForm
from ...models import Task, TaskAttachment, TaskChecklist, TaskMember


TASK_CHECKLIST_SECTION = {
    "title": "Task Checklist",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "name", "label": "Checklist Item", "type": "text", "required": True},
        {"name": "order", "label": "Order", "type": "number", "required": False, "min": 0},
        {"name": "is_completed", "label": "Done", "type": "checkbox", "required": False},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False},
    ],
}

TASK_ATTACHMENTS_SECTION = {
    "title": "Attachments",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "file", "label": "File", "type": "file", "required": True},
        {"name": "file_name", "label": "File Name", "type": "text", "required": False},
        {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False},
    ],
}

TASK_MEMBERS_SECTION = {
    "title": "Task Members",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "user", "label": "User", "type": "select", "required": True, "url_name": "user_select"},
        {"name": "role", "label": "Role", "type": "static_select", "required": True, "options": TaskMember._meta.get_field("role").choices},
    ],
}

def _sanitize_task_code_prefix(value: str) -> str:
    cleaned = re.sub(r"[^A-Z0-9]+", "-", (value or "").upper()).strip("-")
    return cleaned[:12] or "TASK"


def _generate_task_code(task: Task) -> str:
    prefix_seed = ""
    if task.project_id and task.project and task.project.code:
        prefix_seed = task.project.code
    elif task.module_id and task.module and task.module.name:
        prefix_seed = task.module.name
    else:
        prefix_seed = "TASK"

    prefix = _sanitize_task_code_prefix(prefix_seed)
    latest_code = (
        Task.objects.filter(code__startswith=f"{prefix}-")
        .exclude(pk=task.pk)
        .order_by("-id")
        .values_list("code", flat=True)
        .first()
    )
    next_number = 1
    if latest_code:
        try:
            next_number = int(str(latest_code).rsplit("-", 1)[-1]) + 1
        except (TypeError, ValueError):
            next_number = Task.objects.filter(code__startswith=f"{prefix}-").exclude(pk=task.pk).count() + 1
    return f"{prefix}-{next_number:04d}"


def _prepare_task(request, task: Task) -> None:
    task._was_creating = task.pk is None

    if not (task.code or "").strip():
        task.code = _generate_task_code(task)

    if task.status_id and task.status and task.status.is_closed:
        if not task.completed_at:
            task.completed_at = timezone.now()
        if task.progress < 100:
            task.progress = 100
    elif task.completed_at and task.status_id and task.status and not task.status.is_closed:
        task.completed_at = None

    if task.approval_status == "approved" and not task.approved_at:
        task.approved_at = timezone.now()

    if not task.require_approval:
        task.approved_by = None
        task.approved_at = None

    task.sync_billing_fields()

    if not task.is_blocked:
        task.blocked_reason = ""


def _sync_task_checklist_metadata(item: TaskChecklist, row, _task: Task) -> None:
    if item.is_completed:
        item.completed_at = item.completed_at or timezone.now()
    else:
        item.completed_at = None
    item.save(update_fields=["completed_at", "updated_at"])

def _sync_task_attachment_metadata(item: TaskAttachment, row, _task: Task) -> None:
    if item.file:
        item.file_name = item.file_name or item.file.name.rsplit("/", 1)[-1]
        try:
            item.file_size = item.file.size or 0
        except Exception:
            item.file_size = item.file_size or 0
        item.save(update_fields=["file_name", "file_size", "updated_at"])


TASK_CHECKLIST_RELATION = RelatedDynamicSectionConfig(
    section_name="task_checklist",
    related_model=TaskChecklist,
    parent_field="task",
    fields=["name", "order", "is_completed", "remarks"],
    required_fields=["name"],
    bool_fields=["is_completed"],
    empty_check_fields=["name", "remarks"],
    order_by="order",
    save_transformers={
        "name": lambda value: (value or "").strip(),
        "order": lambda value: int(value) if str(value).strip() else 0,
        "remarks": lambda value: (value or "").strip(),
    },
    row_save_hook=_sync_task_checklist_metadata,
)

TASK_ATTACHMENTS_RELATION = RelatedDynamicSectionConfig(
    section_name="task_attachments",
    related_model=TaskAttachment,
    parent_field="task",
    fields=["file", "file_name", "remarks"],
    required_fields=["file"],
    bool_fields=[],
    empty_check_fields=["file", "file_name", "remarks"],
    include_files=True,
    order_by="-created_at",
    save_transformers={
        "file_name": lambda value: (value or "").strip(),
        "remarks": lambda value: (value or "").strip(),
    },
    row_save_hook=_sync_task_attachment_metadata,
)

TASK_MEMBERS_RELATION = RelatedDynamicSectionConfig(
    section_name="task_members",
    related_model=TaskMember,
    parent_field="task",
    fields=["user", "role"],
    required_fields=["user", "role"],
    bool_fields=[],
    empty_check_fields=["user"],
    order_by="id",
    save_transformers={
        "user": lambda value: (value or "").strip(),
        "role": lambda value: (value or "").strip(),
    },
)

_save_task_checklist = build_related_section_saver(TASK_CHECKLIST_RELATION)
_load_task_checklist = build_related_section_loader(TASK_CHECKLIST_RELATION)
_save_task_attachments = build_related_section_saver(TASK_ATTACHMENTS_RELATION)
_load_task_attachments = build_related_section_loader(TASK_ATTACHMENTS_RELATION)
_save_task_members = build_related_section_saver(TASK_MEMBERS_RELATION)
_load_task_members = build_related_section_loader(TASK_MEMBERS_RELATION)


def _clone_checklist_template(task: Task) -> None:
    if not task.checklist_template_id:
        return
    if task.checklist_items.exists():
        return

    template_items = task.checklist_template.items.order_by("order", "name")
    TaskChecklist.objects.bulk_create(
        [
            TaskChecklist(
                task=task,
                template_item=item,
                name=item.name,
                order=item.order,
                is_completed=False,
                remarks=item.remarks,
            )
            for item in template_items
        ]
    )


def _post_save_task(_request, task: Task) -> None:
    _clone_checklist_template(task)


register_entity(
    EntityConfig(
        name="task",
        url_path="tasks",
        verbose_name="Task",
        model=Task,
        form_class=TaskForm,
        datatable_view=TaskDataTableView,
        show_actions=False,
        fields=[],
        tabs=[
            {
                "key": "basic",
                "label": "Basic",
                "show_save": False,
                "fields": [
                    {
                        "name": "code",
                        "label": "Task Code",
                        "type": "text",
                        "required": False,
                        "col": 4,
                        "update_only": True,
                        "attributes": {"readonly": "readonly"},
                    },
                    {"name": "title", "label": "Title", "type": "text", "required": True, "col": 8},
                    {"name": "project", "label": "Project", "type": "select", "required": False, "col": 6, "url_name": "project_select"},
                    {"name": "epic", "label": "Epic", "type": "select", "required": False, "col": 6, "url_name": "project_epic_select"},
                    {"name": "module", "label": "Module", "type": "select", "required": False, "col": 6, "url_name": "task_module_select"},
                    {"name": "task_type", "label": "Task Type", "type": "select", "required": False, "col": 4, "url_name": "task_type_select"},
                    {"name": "status", "label": "Status", "type": "select", "required": True, "col": 4, "url_name": "task_status_select"},
                    {"name": "assignee", "label": "Assigned To", "type": "select", "required": False, "col": 4, "url_name": "user_select"},
                    {"name": "team", "label": "Team", "type": "select", "required": False, "col": 6, "url_name": "team_select"},
                    {"name": "parent_task", "label": "Parent Task", "type": "select", "required": False, "col": 6, "url_name": "task_select"},
                    {"name": "labels", "label": "Labels", "type": "select", "required": False, "col": 12, "url_name": "task_label_select", "multiple": True},
                    {
                        "name": "description",
                        "label": "Description",
                        "type": "richtext",
                        "required": False,
                        "col": 12,
                        "placeholder": "Write the task scope, steps, links, and delivery notes...",
                    },
                ],
            },
            {
                "key": "planning",
                "label": "Planning",
                "show_save": False,
                "fields": [
                    {"name": "priority", "label": "Priority", "type": "static_select", "required": True, "col": 4, "options": Task._meta.get_field("priority").choices},
                    {"name": "severity", "label": "Severity", "type": "static_select", "required": True, "col": 4, "options": Task._meta.get_field("severity").choices},
                    {"name": "progress", "label": "Progress %", "type": "number", "required": False, "col": 4, "min": 0, "max": 100, "step": "0.01"},
                    {"name": "start_date", "label": "Start Date", "type": "date", "required": False, "col": 4},
                    {"name": "due_date", "label": "Due Date", "type": "date", "required": False, "col": 4},
                    {"name": "completed_at", "label": "Completed At", "type": "datetime", "required": False, "col": 4},
                    {"name": "estimated_hours", "label": "Estimated Hours", "type": "number", "required": False, "col": 4, "min": 0, "step": "0.25"},
                    {"name": "logged_hours", "label": "Logged Hours", "type": "number", "required": False, "col": 4, "min": 0, "step": "0.25"},
                    {"name": "is_active", "label": "Is Active", "type": "checkbox", "required": False, "col": 4},
                ],
            },
            {
                "key": "billing",
                "label": "Billing",
                "show_save": False,
                "fields": [
                    {"name": "is_billable", "label": "Is Billable", "type": "checkbox", "required": False, "col": 3},
                    {"name": "billing_type", "label": "Billing Type", "type": "static_select", "required": True, "col": 3, "options": Task._meta.get_field("billing_type").choices},
                    {"name": "billable_to", "label": "Billable To", "type": "static_select", "required": True, "col": 3, "options": Task._meta.get_field("billable_to").choices},
                    {"name": "billing_status", "label": "Billing Status", "type": "static_select", "required": True, "col": 3, "options": Task._meta.get_field("billing_status").choices},
                    {"name": "billing_company_name", "label": "Client / External Party", "type": "text", "required": False, "col": 6},
                    {"name": "billable_department", "label": "Billable Department", "type": "select", "required": False, "col": 3, "url_name": "department_select"},
                    {"name": "currency", "label": "Currency", "type": "select", "required": False, "col": 3, "url_name": "currency_select"},
                    {"name": "rate_per_hour", "label": "Rate Per Hour", "type": "number", "required": False, "col": 3, "min": 0, "step": "0.01"},
                    {"name": "fixed_amount", "label": "Fixed / Per Task Amount", "type": "number", "required": False, "col": 3, "min": 0, "step": "0.01"},
                    {"name": "invoice_reference", "label": "Invoice Ref", "type": "text", "required": False, "col": 6},
                ],
            },
            {
                "key": "workflow",
                "label": "Workflow",
                "show_save": False,
                "fields": [
                    {"name": "depends_on", "label": "Depends On", "type": "select", "required": False, "col": 6, "url_name": "task_select", "multiple": True},
                    {"name": "blocked_by", "label": "Blocked By", "type": "select", "required": False, "col": 6, "url_name": "task_select", "multiple": True},
                    {"name": "is_blocked", "label": "Is Blocked", "type": "checkbox", "required": False, "col": 4},
                    {"name": "require_approval", "label": "Require Approval", "type": "checkbox", "required": False, "col": 4},
                    {"name": "approval_status", "label": "Approval Status", "type": "static_select", "required": True, "col": 4, "options": Task._meta.get_field("approval_status").choices},
                    {"name": "approved_by", "label": "Approved By", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
                    {"name": "approved_at", "label": "Approved At", "type": "datetime", "required": False, "col": 6},
                    {"name": "blocked_reason", "label": "Blocked Reason", "type": "textarea", "required": False, "col": 12},
                    {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False, "col": 12},
                ],
            },
            {
                "key": "people",
                "label": "People",
                "show_save": False,
                "fields": [
                    {"name": "assignee", "label": "Assigned To", "type": "select", "required": False, "col": 6, "url_name": "user_select"},
                    {"name": "team", "label": "Team", "type": "select", "required": False, "col": 6, "url_name": "team_select"},
                ],
                "sections": ["task_members"],
            },
            {
                "key": "checklist",
                "label": "Checklist",
                "show_save": False,
                "fields": [
                    {"name": "checklist_template", "label": "Checklist Template", "type": "select", "required": False, "col": 12, "url_name": "checklist_select"},
                ],
                "sections": ["task_checklist"],
            },
            {
                "key": "attachments",
                "label": "Attachments",
                "show_save": False,
                "fields": [],
                "sections": ["task_attachments"],
            },
        ],
        dynamic_sections={
            "task_checklist": TASK_CHECKLIST_SECTION,
            "task_attachments": TASK_ATTACHMENTS_SECTION,
            "task_members": TASK_MEMBERS_SECTION,
        },
        dynamic_sections_loader=lambda task, request=None: {
            **_load_task_checklist(task, request),
            **_load_task_attachments(task, request),
            **_load_task_members(task, request),
        },
        dynamic_sections_saver=lambda request, task: (
            _save_task_checklist(request, task),
            _save_task_attachments(request, task),
            _save_task_members(request, task),
        ),
        pre_save=_prepare_task,
        post_save=_post_save_task,
        datatable_columns=[
            {"name": key, "title": key.replace("_", " ").title()}
            for key, _accessor in TASK_COLUMNS
            if key != "id"
        ]
        + [
            {
                "name": "id",
                "title": "Actions",
                "orderable": False,
                "searchable": False,
                "render": (
                    "function(data,type,row){return renderActionButtons((row && row.id) || data, {"
                    "view: true, "
                    "edit: '/core/tasks/{id}/update/', "
                    "delete: '/core/tasks/{id}/delete/', "
                    "detail: '/core/tasks/{id}/detail/', "
                    "modal_id: '#taskModal', "
                    "title: 'Edit Task', "
                    "view_title: 'View Task', "
                    "extra_actions: [{"
                    "label: 'Open', "
                    "title: 'Open Task', "
                    "icon_class: 'fas fa-external-link-alt', "
                    "class_name: 'btn-outline-secondary', "
                    "href_url: '/core/tasks/{id}/view/'"
                    "}]"
                    "}, row || {});}"
                ),
            }
        ],
        reset_defaults={
            "priority": "medium",
            "severity": "medium",
            "billing_type": "none",
            "billable_to": "internal",
            "billing_status": "not_billable",
            "rate_per_hour": "0.00",
            "fixed_amount": "0.00",
            "progress": "0.00",
            "approval_status": "pending",
            "is_active": True,
        },
        datatable_options={
            "page_length": 25,
            "length_menu": [10, 25, 50, 100],
            "scroll_x": True,
            "responsive": False,
            "dom": "Bfrtip",
            "buttons": ["copy", "csv", "excel", "pdf", "print", "colvis"],
        },
        select_search_fields=[
            "code",
            "title",
            "project__name",
            "epic__name",
            "assignee__username",
        ],
        select_label_func=lambda obj: obj.code and f"{obj.code} - {obj.title}" or obj.title,
    )
)

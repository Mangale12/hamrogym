from decimal import Decimal, InvalidOperation

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views import View

from .models import (
    ChecklistItem,
    Task,
    TaskAttachment,
    TaskBilling,
    TaskBillingRecordStatus,
    TaskChecklist,
    TaskComment,
    TaskMember,
    TaskStatus,
    TimeLog,
    TimeLogApprovalStatus,
    TimeLogRateType,
    generate_task_billings,
)


def _redirect_to_task_tab(pk, tab_id="comments"):
    return redirect(f"{reverse('task_view', kwargs={'pk': pk})}#{tab_id}")


def _is_ajax(request) -> bool:
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _serialize_errors(errors):
    serialized = {}
    for key, value in (errors or {}).items():
        if isinstance(value, (list, tuple)):
            serialized[key] = [str(item) for item in value]
        else:
            serialized[key] = [str(value)]
    return serialized


def _validation_error_payload(exc: ValidationError):
    if hasattr(exc, "message_dict"):
        return _serialize_errors(exc.message_dict)
    return {"__all__": [str(message) for message in getattr(exc, "messages", [str(exc)])]}


def _task_action_success(request, pk, *, tab_id, message):
    if _is_ajax(request):
        return JsonResponse(
            {
                "success": True,
                "message": message,
                "tab_id": tab_id,
                "task_url": reverse("task_view", kwargs={"pk": pk}),
            }
        )
    return _redirect_to_task_tab(pk, tab_id)


def _task_action_error(request, pk, *, tab_id, message, errors=None, status=400):
    if _is_ajax(request):
        return JsonResponse(
            {
                "success": False,
                "message": message,
                "errors": _serialize_errors(errors),
                "tab_id": tab_id,
            },
            status=status,
        )
    return _redirect_to_task_tab(pk, tab_id)


class ChecklistTemplateItemsView(LoginRequiredMixin, View):
    def get(self, request):
        template_id = (request.GET.get("template_id") or "").strip()
        if not template_id.isdigit():
            return JsonResponse({"success": True, "items": []})

        items = (
            ChecklistItem.objects.filter(checklist_id=template_id)
            .order_by("order", "name")
            .values("name", "order", "remarks")
        )
        return JsonResponse(
            {
                "success": True,
                "items": [
                    {
                        "name": item["name"],
                        "order": item["order"],
                        "remarks": item["remarks"] or "",
                        "is_completed": False,
                    }
                    for item in items
                ],
            }
        )


class TaskDetailPageView(LoginRequiredMixin, View):
    template_name = "task/task_detail.html"

    def get(self, request, pk):
        task = get_object_or_404(
            Task.objects.select_related(
                "project",
                "epic",
                "module",
                "task_type",
                "status",
                "assignee",
                "team",
                "currency",
                "billable_department",
            )
            .prefetch_related(
                "labels",
                "checklist_items",
                "attachments",
                "billings__user",
                "billings__approved_by",
                "billings__currency",
                "members__user",
                "comments__user",
                "comments__attachment",
                "comments__replies__user",
                "comments__replies__attachment",
                "time_logs__user",
                "activities__user",
            ),
            pk=pk,
        )
        role_choices = TaskMember._meta.get_field("role").choices
        root_comments = [comment for comment in task.comments.all() if not comment.parent_comment_id]
        return render(
            request,
            self.template_name,
            {
                "task": task,
                "role_choices": role_choices,
                "root_comments": root_comments,
                "time_log_approval_choices": TimeLogApprovalStatus.choices,
                "time_log_rate_type_choices": TimeLogRateType.choices,
                "task_billing_status_choices": TaskBillingRecordStatus.choices,
            },
        )


class TaskChecklistAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        name = (request.POST.get("name") or "").strip()
        order = request.POST.get("order") or ""
        remarks = (request.POST.get("remarks") or "").strip()
        if not name:
            return _task_action_error(
                request,
                pk,
                tab_id="checklist",
                message="Checklist item name is required.",
                errors={"name": ["Checklist item name is required."]},
            )

        TaskChecklist.objects.create(
            task=task,
            name=name,
            order=int(order) if str(order).strip().isdigit() else 0,
            remarks=remarks,
        )
        return _task_action_success(request, pk, tab_id="checklist", message="Checklist item added successfully.")


class TaskChecklistUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, item_id):
        task = get_object_or_404(Task, pk=pk)
        item = get_object_or_404(TaskChecklist, pk=item_id, task=task)
        item.name = (request.POST.get("name") or "").strip()
        order = request.POST.get("order")
        if str(order).strip().isdigit():
            item.order = int(order)
        item.remarks = (request.POST.get("remarks") or "").strip()
        is_completed = (request.POST.get("is_completed") or "").lower() in {"1", "true", "on", "yes"}
        item.is_completed = is_completed
        item.completed_at = timezone.now() if is_completed else None
        if not item.name:
            return _task_action_error(
                request,
                pk,
                tab_id="checklist",
                message="Checklist item name is required.",
                errors={"name": ["Checklist item name is required."]},
            )
        item.save()
        return _task_action_success(request, pk, tab_id="checklist", message="Checklist item updated successfully.")


class TaskMemberAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        user_id = request.POST.get("user") or ""
        role = (request.POST.get("role") or "").strip()
        if not user_id.isdigit():
            return _task_action_error(
                request,
                pk,
                tab_id="members",
                message="Please choose a user.",
                errors={"user": ["Please choose a user."]},
            )

        TaskMember.objects.update_or_create(
            task=task,
            user_id=int(user_id),
            defaults={"role": role or TaskMember._meta.get_field("role").choices[0][0]},
        )
        return _task_action_success(request, pk, tab_id="members", message="Task member saved successfully.")


class TaskCommentAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        content = (request.POST.get("content") or "").strip()
        attachment_id = (request.POST.get("attachment") or "").strip()
        parent_comment_id = (request.POST.get("parent_comment") or "").strip()

        if not content:
            return _task_action_error(
                request,
                pk,
                tab_id="comments",
                message="Comment content is required.",
                errors={"content": ["Comment content is required."]},
            )

        attachment = None
        if attachment_id.isdigit():
            attachment = get_object_or_404(TaskAttachment, pk=int(attachment_id), task=task)

        parent_comment = None
        if parent_comment_id.isdigit():
            parent_comment = get_object_or_404(TaskComment, pk=int(parent_comment_id), task=task)

        TaskComment.objects.create(
            task=task,
            user=request.user,
            content=content,
            attachment=attachment,
            parent_comment=parent_comment,
        )
        return _task_action_success(request, pk, tab_id="comments", message="Comment saved successfully.")


class TaskCommentUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, comment_id):
        task = get_object_or_404(Task, pk=pk)
        comment = get_object_or_404(TaskComment, pk=comment_id, task=task, user=request.user)
        content = (request.POST.get("content") or "").strip()
        attachment_id = (request.POST.get("attachment") or "").strip()

        if not content:
            return _task_action_error(
                request,
                pk,
                tab_id="comments",
                message="Comment content is required.",
                errors={"content": ["Comment content is required."]},
            )

        comment.content = content
        if attachment_id.isdigit():
            comment.attachment = get_object_or_404(TaskAttachment, pk=int(attachment_id), task=task)
        else:
            comment.attachment = None
        comment.save(update_fields=["content", "attachment", "updated_at"])
        return _task_action_success(request, pk, tab_id="comments", message="Comment updated successfully.")


class TaskTimeLogAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        user_id = request.POST.get("user") or ""
        started_at_raw = request.POST.get("started_at") or ""
        stopped_at_raw = request.POST.get("stopped_at") or ""
        duration_hours = request.POST.get("duration_hours") or ""
        description = (request.POST.get("description") or "").strip()
        is_billable = (request.POST.get("is_billable") or "").lower() in {"1", "true", "on", "yes"}
        rate_type = (request.POST.get("rate_type") or "").strip() or TimeLogRateType.NORMAL
        hourly_rate_raw = (request.POST.get("hourly_rate") or "").strip()

        started_at = parse_datetime(started_at_raw) if started_at_raw else None
        stopped_at = parse_datetime(stopped_at_raw) if stopped_at_raw else None
        duration = None
        hourly_rate = None
        if duration_hours:
            try:
                duration = timezone.timedelta(hours=float(duration_hours))
            except Exception:
                duration = None
        if hourly_rate_raw:
            try:
                hourly_rate = Decimal(hourly_rate_raw)
            except (InvalidOperation, TypeError, ValueError):
                hourly_rate = None
        if started_at and stopped_at and not duration:
            duration = stopped_at - started_at

        errors = {}
        if not user_id.isdigit():
            errors["user"] = ["Please choose a user."]
        if not started_at:
            errors["started_at"] = ["Start time is required."]
        if not stopped_at:
            errors["stopped_at"] = ["Stop time is required."]
        if duration_hours and duration is None:
            errors["duration_hours"] = ["Enter a valid duration in hours."]
        if hourly_rate_raw and hourly_rate is None:
            errors["hourly_rate"] = ["Enter a valid hourly rate."]

        if errors:
            return _task_action_error(
                request,
                pk,
                tab_id="timelog",
                message="Please correct the highlighted time log fields.",
                errors=errors,
            )

        try:
            TimeLog.objects.create(
                task=task,
                user_id=int(user_id),
                started_at=started_at,
                stopped_at=stopped_at,
                duration=duration,
                description=description,
                is_billable=is_billable,
                hourly_rate=hourly_rate or 0,
                rate_type=rate_type,
            )
        except ValidationError as exc:
            return _task_action_error(
                request,
                pk,
                tab_id="timelog",
                message="Unable to save the time log.",
                errors=_validation_error_payload(exc),
            )

        return _task_action_success(request, pk, tab_id="timelog", message="Time log added successfully.")


class TaskTimeLogApprovalView(LoginRequiredMixin, View):
    def post(self, request, pk, log_id):
        task = get_object_or_404(Task, pk=pk)
        time_log = get_object_or_404(TimeLog, pk=log_id, task=task)
        approval_status = (request.POST.get("approval_status") or "").strip()
        approved_hours_raw = (request.POST.get("approved_hours") or "").strip()

        if approval_status not in {
            TimeLogApprovalStatus.PENDING,
            TimeLogApprovalStatus.APPROVED,
            TimeLogApprovalStatus.REJECTED,
        }:
            return _task_action_error(
                request,
                pk,
                tab_id="timelog",
                message="Choose a valid approval status.",
                errors={"approval_status": ["Choose a valid approval status."]},
            )

        approved_hours = approved_hours_raw or 0
        time_log.approval_status = approval_status
        time_log.approved_by = request.user if approval_status == TimeLogApprovalStatus.APPROVED else None
        time_log.approved_hours = approved_hours if approval_status == TimeLogApprovalStatus.APPROVED else 0
        if approval_status != TimeLogApprovalStatus.APPROVED:
            time_log.task_billing = None

        try:
            time_log.save()
        except ValidationError as exc:
            return _task_action_error(
                request,
                pk,
                tab_id="timelog",
                message="Unable to update the time log approval.",
                errors=_validation_error_payload(exc),
            )

        return _task_action_success(request, pk, tab_id="timelog", message="Time log approval updated successfully.")


class TaskBillingGenerateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        generated = generate_task_billings(task, generated_by=request.user)
        if not generated:
            return _task_action_error(
                request,
                pk,
                tab_id="billing",
                message="No eligible billing records were found to generate.",
                errors={"__all__": ["Approve billable time logs first, or set a fixed/per-task amount."]},
            )
        return _task_action_success(
            request,
            pk,
            tab_id="billing",
            message=f"Generated {len(generated)} billing record(s) successfully.",
        )


class TaskBillingStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, billing_id):
        task = get_object_or_404(Task, pk=pk)
        billing = get_object_or_404(TaskBilling, pk=billing_id, task=task)
        status = (request.POST.get("status") or "").strip()
        if status not in {choice[0] for choice in TaskBillingRecordStatus.choices}:
            return _task_action_error(
                request,
                pk,
                tab_id="billing",
                message="Choose a valid billing status.",
                errors={"status": ["Choose a valid billing status."]},
            )

        billing.status = status
        if status == TaskBillingRecordStatus.APPROVED:
            billing.approved_by = request.user
            billing.approved_at = timezone.now()
        elif status != TaskBillingRecordStatus.APPROVED:
            billing.approved_by = None
            billing.approved_at = None
        billing.save()
        return _task_action_success(request, pk, tab_id="billing", message="Billing status updated successfully.")


class TaskBoardView(LoginRequiredMixin, View):
    template_name = "task/task_board.html"

    def get(self, request):
        statuses = list(TaskStatus.objects.all().order_by("sequence", "name", "id"))
        tasks = (
            Task.objects.select_related("status", "assignee")
            .prefetch_related("labels")
            .order_by("status__sequence", "priority", "due_date", "title")
        )
        grouped = {status.id: [] for status in statuses}
        for task in tasks:
            if task.status_id in grouped:
                grouped[task.status_id].append(task)
            else:
                grouped.setdefault(task.status_id, []).append(task)
        columns = [
            {"status": status, "tasks": grouped.get(status.id, [])}
            for status in statuses
        ]
        return render(
            request,
            self.template_name,
            {
                "columns": columns,
            },
        )


class TaskKanbanStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        task_id = request.POST.get("task_id") or ""
        status_id = request.POST.get("status_id") or ""
        if not (task_id.isdigit() and status_id.isdigit()):
            return JsonResponse({"success": False, "message": "Invalid task/status."}, status=400)

        task = get_object_or_404(Task, pk=int(task_id))
        status = get_object_or_404(TaskStatus, pk=int(status_id))
        task.status = status
        task.save(update_fields=["status", "updated_at"])
        return JsonResponse({"success": True})

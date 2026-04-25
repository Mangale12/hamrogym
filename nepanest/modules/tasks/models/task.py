from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.choices import APPROVAL_STATUS_CHOICES, PRIORITY_CHOICES
from nepanest.common.mixins.erp import ERPBaseModel


class TaskSeverity(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"

class TaskMemberRole(models.TextChoices):
    MEMBER = "member", "Member"
    WATCHER = "watcher", "Watcher"


class TaskBillingType(models.TextChoices):
    NONE = "none", "None"
    HOURLY = "hourly", "Hourly"
    FIXED = "fixed", "Fixed"
    PER_TASK = "per_task", "Per Task"


class TaskBillingStatus(models.TextChoices):
    NOT_BILLABLE = "not_billable", "Not Billable"
    UNBILLED = "unbilled", "Unbilled"
    BILLED = "billed", "Billed"
    PAID = "paid", "Paid"


class TaskBillableTo(models.TextChoices):
    CLIENT = "client", "Client"
    DEPARTMENT = "department", "Department"
    INTERNAL = "internal", "Internal"


class TimeLogApprovalStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class TimeLogRateType(models.TextChoices):
    NORMAL = "normal", "Normal"
    OVERTIME = "overtime", "Overtime"


class TaskBillingRecordStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    APPROVED = "approved", "Approved"
    INVOICED = "invoiced", "Invoiced"
    PAID = "paid", "Paid"


class Task(ERPBaseModel):
    code = models.CharField(max_length=30, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey("Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    epic = models.ForeignKey("ProjectEpic", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    module = models.ForeignKey("TaskModule", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    checklist_template = models.ForeignKey(
        "Checklist",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    parent_task = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subtasks")
    task_type = models.ForeignKey("TaskType", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    status = models.ForeignKey("TaskStatus", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    team = models.ForeignKey("hr.Team", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    labels = models.ManyToManyField("TaskLabel", related_name="tasks", blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    severity = models.CharField(max_length=20, choices=TaskSeverity.choices, default=TaskSeverity.MEDIUM)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    logged_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_billable = models.BooleanField(default=False)
    billing_company_name = models.CharField(max_length=255, blank=True)
    billing_type = models.CharField(max_length=20, choices=TaskBillingType.choices, default=TaskBillingType.NONE)
    rate_per_hour = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_currency_tasks",
    )
    billable_to = models.CharField(max_length=20, choices=TaskBillableTo.choices, default=TaskBillableTo.INTERNAL)
    billable_department = models.ForeignKey(
        "hr.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billable_tasks",
    )
    billing_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    billing_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    billing_status = models.CharField(
        max_length=20,
        choices=TaskBillingStatus.choices,
        default=TaskBillingStatus.NOT_BILLABLE,
    )
    invoice_reference = models.CharField(max_length=100, blank=True)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    require_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_tasks",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default="pending")
    depends_on = models.ManyToManyField("self", symmetrical=False, related_name="dependents", blank=True)
    blocked_by = models.ManyToManyField("self", symmetrical=False, related_name="blockers", blank=True)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True)

    class Meta:
        app_label = "task"
        ordering = ["-created_at", "code", "title"]

    def __str__(self) -> str:
        return f"{self.code} - {self.title}" if self.code else self.title

    @staticmethod
    def _quantize_amount(value) -> Decimal:
        return Decimal(value or 0).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def get_effective_hourly_rate(self, *, user=None, work_date=None) -> Decimal:
        if user is not None:
            employee = getattr(user, "employee_profile", None)
            if employee is not None:
                effective_date = work_date or self.start_date
                rate_qs = EmployeeRate.objects.filter(employee=employee)
                if effective_date:
                    rate_qs = rate_qs.filter(effective_from__lte=effective_date)
                employee_rate = rate_qs.order_by("-effective_from", "-id").first()
                if employee_rate and employee_rate.rate_per_hour > 0:
                    return self._quantize_amount(employee_rate.rate_per_hour)
        if self.rate_per_hour and self.rate_per_hour > 0:
            return self._quantize_amount(self.rate_per_hour)
        if self.billing_rate and self.billing_rate > 0:
            return self._quantize_amount(self.billing_rate)
        return Decimal("0.00")

    def calculate_billing_amount(self) -> Decimal:
        if not self.is_billable:
            return Decimal("0.00")
        if self.billing_type == TaskBillingType.HOURLY:
            if not self.pk:
                return self._quantize_amount(Decimal("0.00"))
            approved_logs = self.time_logs.filter(
                is_billable=True,
                approval_status=TimeLogApprovalStatus.APPROVED,
            ).only("approved_hours", "hours_spent", "hourly_rate")
            total_amount = Decimal("0.00")
            for log in approved_logs:
                approved_hours = Decimal(log.approved_hours or 0) or Decimal(log.hours_spent or 0)
                total_amount += approved_hours * Decimal(log.hourly_rate or 0)
            return self._quantize_amount(total_amount)
        if self.billing_type in {TaskBillingType.FIXED, TaskBillingType.PER_TASK}:
            return self._quantize_amount(self.fixed_amount or self.billing_amount)
        return Decimal("0.00")

    def sync_billing_fields(self) -> None:
        if not self.is_billable or self.billing_type == TaskBillingType.NONE:
            self.billing_type = TaskBillingType.NONE
            self.billing_status = TaskBillingStatus.NOT_BILLABLE
            self.invoice_reference = ""
            self.billing_rate = Decimal("0.00")
            self.billing_amount = Decimal("0.00")
            return

        if self.billing_status == TaskBillingStatus.NOT_BILLABLE:
            self.billing_status = TaskBillingStatus.UNBILLED

        self.rate_per_hour = self._quantize_amount(self.rate_per_hour or self.billing_rate)
        self.fixed_amount = self._quantize_amount(self.fixed_amount or self.billing_amount)
        self.billing_rate = self.rate_per_hour
        self.billing_amount = self.calculate_billing_amount()
        if self.billable_to != TaskBillableTo.DEPARTMENT:
            self.billable_department = None

    def clean(self):
        errors = {}

        if self.start_date and self.due_date and self.due_date < self.start_date:
            errors["due_date"] = "Due date must be on or after start date."

        if self.progress is not None and (self.progress < 0 or self.progress > 100):
            errors["progress"] = "Progress must be between 0 and 100."

        if self.estimated_hours is not None and self.estimated_hours < 0:
            errors["estimated_hours"] = "Estimated hours cannot be negative."

        if self.logged_hours is not None and self.logged_hours < 0:
            errors["logged_hours"] = "Logged hours cannot be negative."

        if self.rate_per_hour is not None and self.rate_per_hour < 0:
            errors["rate_per_hour"] = "Rate per hour cannot be negative."

        if self.fixed_amount is not None and self.fixed_amount < 0:
            errors["fixed_amount"] = "Fixed amount cannot be negative."

        if self.billing_rate is not None and self.billing_rate < 0:
            errors["billing_rate"] = "Billing rate cannot be negative."

        if self.billing_amount is not None and self.billing_amount < 0:
            errors["billing_amount"] = "Billing amount cannot be negative."

        if self.is_blocked and not (self.blocked_reason or "").strip():
            errors["blocked_reason"] = "Blocked reason is required when the task is marked as blocked."

        if self.epic_id and self.project_id and self.epic and self.epic.project_id != self.project_id:
            errors["epic"] = "Selected epic must belong to the chosen project."

        if (
            self.module_id
            and self.project_id
            and self.project
            and self.project.module_id
            and self.project.module_id != self.module_id
        ):
            errors["module"] = "Selected module must match the project's module."

        if self.checklist_template_id and self.checklist_template:
            # Allow cross-project/module checklist templates to keep task saves flexible.
            pass

        if self.approval_status == "approved":
            if not self.approved_by_id:
                errors["approved_by"] = "Approved by is required when approval status is approved."
            if not self.approved_at:
                errors["approved_at"] = "Approved at is required when approval status is approved."

        if self.is_billable:
            if self.billing_type == TaskBillingType.NONE:
                errors["billing_type"] = "Choose a billing type for billable tasks."
            if self.billing_type in {TaskBillingType.FIXED, TaskBillingType.PER_TASK} and self.fixed_amount <= 0:
                errors["fixed_amount"] = "Fixed amount must be greater than zero for fixed or per-task billing."
            if self.billable_to == TaskBillableTo.CLIENT and not (self.billing_company_name or "").strip():
                errors["billing_company_name"] = "Client name is required when billable to client."
            if self.billable_to == TaskBillableTo.DEPARTMENT and not self.billable_department_id:
                errors["billable_department"] = "Department is required when billable to department."
        elif self.billing_status != TaskBillingStatus.NOT_BILLABLE:
            errors["billing_status"] = "Non-billable tasks must use the Not Billable status."

        if self.billing_status in {TaskBillingStatus.BILLED, TaskBillingStatus.PAID} and not (
            self.invoice_reference or ""
        ).strip():
            errors["invoice_reference"] = "Invoice reference is required when the task is billed or paid."

        if errors:
            raise ValidationError(errors)


class TaskChecklist(ERPBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="checklist_items")
    template_item = models.ForeignKey(
        "ChecklistItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_checklist_items",
    )
    name = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "task"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class TaskMember(ERPBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_memberships")
    role = models.CharField(max_length=20, choices=TaskMemberRole.choices, default=TaskMemberRole.MEMBER)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "task"
        ordering = ["task__title", "user__username", "id"]
        constraints = [
            models.UniqueConstraint(fields=["task", "user", "role"], name="unique_task_member_role"),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.task}"


class TaskAttachment(ERPBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="task_attachments/")
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "task"
        ordering = ["uploaded_at"]

    def __str__(self) -> str:
        return f"Attachment for {self.task.title}"
    

class TaskComment(ERPBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_comments")
    content = models.TextField()
    attachment = models.ForeignKey(TaskAttachment, on_delete=models.SET_NULL, null=True, blank=True, related_name="comments")
    parent_comment = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")

    class Meta:
        app_label = "task"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.user.username} on {self.task.title}"


class TaskActivity(ERPBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="activities")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_activities")
    action = models.CharField(max_length=255)
    field_name = models.CharField(max_length=255)
    new_value = models.TextField(null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)

    class Meta:
        app_label = "task"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Activity by {self.user.username} on {self.task.title}: {self.action}"


class EmployeeRate(ERPBaseModel):
    employee = models.ForeignKey("hr.Employee", on_delete=models.CASCADE, related_name="task_rates")
    rate_per_hour = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_rate_currencies",
    )
    effective_from = models.DateField()

    class Meta:
        app_label = "task"
        ordering = ["employee__employee_id", "-effective_from", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["employee", "effective_from"], name="unique_employee_rate_effective_from"),
        ]

    def __str__(self) -> str:
        return f"{self.employee} - {self.rate_per_hour}"

    def clean(self):
        if self.rate_per_hour is not None and self.rate_per_hour < 0:
            raise ValidationError({"rate_per_hour": "Rate per hour cannot be negative."})


class TimeLog(ERPBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="time_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="time_logs")
    work_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    duration = models.DurationField()
    started_at = models.DateTimeField()
    stopped_at = models.DateTimeField()
    hours_spent = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_billable = models.BooleanField(default=False)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    approved_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    approval_status = models.CharField(max_length=20, choices=TimeLogApprovalStatus.choices, default=TimeLogApprovalStatus.PENDING)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_task_time_logs",
    )
    rate_type = models.CharField(max_length=20, choices=TimeLogRateType.choices, default=TimeLogRateType.NORMAL)
    task_billing = models.ForeignKey(
        "TaskBilling",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_logs",
    )

    class Meta:
        app_label = "task"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"Time log for {self.task.title} by {self.user.username}"

    def clean(self):
        errors = {}
        if self.started_at and self.stopped_at and self.stopped_at < self.started_at:
            errors["stopped_at"] = "Stopped at must be on or after started at."
        if self.duration is not None and self.duration.total_seconds() < 0:
            errors["duration"] = "Duration cannot be negative."
        if self.hours_spent is not None and self.hours_spent < 0:
            errors["hours_spent"] = "Hours spent cannot be negative."
        if self.hourly_rate is not None and self.hourly_rate < 0:
            errors["hourly_rate"] = "Hourly rate cannot be negative."
        if self.amount is not None and self.amount < 0:
            errors["amount"] = "Amount cannot be negative."
        if self.approved_hours is not None and self.approved_hours < 0:
            errors["approved_hours"] = "Approved hours cannot be negative."
        if self.hours_spent is not None and self.approved_hours is not None and self.approved_hours > self.hours_spent:
            errors["approved_hours"] = "Approved hours cannot be greater than hours spent."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.started_at and self.stopped_at:
            self.duration = self.stopped_at - self.started_at
            self.work_date = self.started_at.date()
            self.start_time = self.started_at.time().replace(microsecond=0)
            self.end_time = self.stopped_at.time().replace(microsecond=0)

        hours_spent = Decimal("0.00")
        if self.duration is not None:
            hours_spent = Task._quantize_amount(Decimal(self.duration.total_seconds()) / Decimal("3600"))
        self.hours_spent = hours_spent

        if self.is_billable and (self.hourly_rate or 0) <= 0:
            self.hourly_rate = self.task.get_effective_hourly_rate(user=self.user, work_date=self.work_date)
        self.hourly_rate = Task._quantize_amount(self.hourly_rate)
        self.amount = Task._quantize_amount(self.hours_spent * self.hourly_rate) if self.is_billable else Decimal("0.00")

        if self.approval_status == TimeLogApprovalStatus.APPROVED:
            self.approved_hours = Task._quantize_amount(self.approved_hours or self.hours_spent)
        elif self.approval_status == TimeLogApprovalStatus.PENDING:
            self.approved_hours = Decimal("0.00")
            self.task_billing = None
        elif self.approval_status == TimeLogApprovalStatus.REJECTED:
            self.approved_hours = Decimal("0.00")
            self.task_billing = None

        self.full_clean()
        super().save(*args, **kwargs)
        sync_task_time_summary(self.task_id)
        sync_task_billing_summary(self.task_id)

    def delete(self, *args, **kwargs):
        task_id = self.task_id
        super().delete(*args, **kwargs)
        sync_task_time_summary(task_id)
        sync_task_billing_summary(task_id)


class TaskBilling(ERPBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="billings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_billing_records",
    )
    total_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    billing_type = models.CharField(max_length=20, choices=TaskBillingType.choices, default=TaskBillingType.HOURLY)
    status = models.CharField(max_length=20, choices=TaskBillingRecordStatus.choices, default=TaskBillingRecordStatus.DRAFT)
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_billing_currencies",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_task_billings",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "task"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.task} - {self.total_amount}"

    def clean(self):
        errors = {}
        if self.total_hours is not None and self.total_hours < 0:
            errors["total_hours"] = "Total hours cannot be negative."
        if self.rate is not None and self.rate < 0:
            errors["rate"] = "Rate cannot be negative."
        if self.total_amount is not None and self.total_amount < 0:
            errors["total_amount"] = "Total amount cannot be negative."
        if self.billing_type == TaskBillingType.NONE:
            errors["billing_type"] = "Billing record must use hourly, fixed, or per-task billing."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.total_hours = Task._quantize_amount(self.total_hours)
        self.rate = Task._quantize_amount(self.rate)
        self.total_amount = Task._quantize_amount(self.total_amount)
        if self.status == TaskBillingRecordStatus.APPROVED and not self.approved_at:
            self.approved_at = timezone.now()
        self.full_clean()
        super().save(*args, **kwargs)
        sync_task_billing_summary(self.task_id)


def sync_task_time_summary(task_id: int) -> None:
    task = Task.objects.filter(pk=task_id).only(
        "id",
        "logged_hours",
        "is_billable",
        "billing_type",
        "rate_per_hour",
        "fixed_amount",
        "billing_rate",
        "billing_amount",
    ).first()
    if not task:
        return

    total_seconds = 0
    for duration in TimeLog.objects.filter(task_id=task_id).values_list("duration", flat=True):
        if duration:
            total_seconds += int(duration.total_seconds())

    logged_hours = (Decimal(total_seconds) / Decimal("3600")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    update_fields = {}

    if task.logged_hours != logged_hours:
        update_fields["logged_hours"] = logged_hours

    if task.is_billable and task.billing_type == TaskBillingType.HOURLY:
        approved_logs = TimeLog.objects.filter(
            task_id=task_id,
            is_billable=True,
            approval_status=TimeLogApprovalStatus.APPROVED,
        ).only("approved_hours", "hours_spent", "hourly_rate")
        approved_amount = Decimal("0.00")
        for log in approved_logs:
            approved_hours = Decimal(log.approved_hours or 0) or Decimal(log.hours_spent or 0)
            approved_amount += approved_hours * Decimal(log.hourly_rate or 0)
        billing_amount = Task._quantize_amount(approved_amount)
        if task.billing_amount != billing_amount:
            update_fields["billing_amount"] = billing_amount
    elif task.is_billable and task.billing_type in {TaskBillingType.FIXED, TaskBillingType.PER_TASK}:
        fixed_amount = Task._quantize_amount(task.fixed_amount or task.billing_amount)
        if task.billing_amount != fixed_amount:
            update_fields["billing_amount"] = fixed_amount

    if update_fields:
        Task.objects.filter(pk=task_id).update(**update_fields)


def sync_task_billing_summary(task_id: int) -> None:
    task = Task.objects.filter(pk=task_id).only("id", "is_billable", "billing_type", "fixed_amount", "billing_status").first()
    if not task:
        return

    if not task.is_billable or task.billing_type == TaskBillingType.NONE:
        Task.objects.filter(pk=task_id).update(
            billing_status=TaskBillingStatus.NOT_BILLABLE,
            billing_amount=Decimal("0.00"),
            updated_at=timezone.now(),
        )
        return

    billings = list(TaskBilling.objects.filter(task_id=task_id).only("status"))
    if not billings:
        status = TaskBillingStatus.UNBILLED
    elif billings and all(billing.status == TaskBillingRecordStatus.PAID for billing in billings):
        status = TaskBillingStatus.PAID
    else:
        status = TaskBillingStatus.BILLED

    Task.objects.filter(pk=task_id).update(billing_status=status, updated_at=timezone.now())


def generate_task_billings(task: Task, *, generated_by=None):
    created_billings = []
    if not task.is_billable or task.billing_type == TaskBillingType.NONE:
        return created_billings

    if task.billing_type == TaskBillingType.HOURLY:
        eligible_logs = list(
            TimeLog.objects.filter(
                task=task,
                is_billable=True,
                approval_status=TimeLogApprovalStatus.APPROVED,
                task_billing__isnull=True,
            )
            .select_related("user")
            .order_by("user_id", "hourly_rate", "id")
        )
        grouped_logs = defaultdict(list)
        for log in eligible_logs:
            grouped_logs[(log.user_id, str(log.hourly_rate))].append(log)

        for (user_id, _rate_key), logs in grouped_logs.items():
            rate = Task._quantize_amount(logs[0].hourly_rate)
            total_hours = sum((Decimal(log.approved_hours or 0) or Decimal(log.hours_spent or 0)) for log in logs)
            total_hours = Task._quantize_amount(total_hours)
            total_amount = Task._quantize_amount(total_hours * rate)
            billing = TaskBilling.objects.create(
                task=task,
                user_id=user_id,
                total_hours=total_hours,
                rate=rate,
                total_amount=total_amount,
                billing_type=TaskBillingType.HOURLY,
                status=TaskBillingRecordStatus.DRAFT,
                currency=task.currency,
                created_by=generated_by,
                updated_by=generated_by,
            )
            TimeLog.objects.filter(pk__in=[log.pk for log in logs]).update(task_billing=billing, updated_at=timezone.now())
            created_billings.append(billing)
    else:
        already_exists = TaskBilling.objects.filter(task=task, billing_type=task.billing_type).exclude(
            status=TaskBillingRecordStatus.PAID
        ).exists()
        if not already_exists:
            amount = Task._quantize_amount(task.fixed_amount)
            billing = TaskBilling.objects.create(
                task=task,
                user=task.assignee,
                total_hours=Decimal("1.00") if task.billing_type == TaskBillingType.PER_TASK else Decimal("0.00"),
                rate=amount,
                total_amount=amount,
                billing_type=task.billing_type,
                status=TaskBillingRecordStatus.DRAFT,
                currency=task.currency,
                created_by=generated_by,
                updated_by=generated_by,
            )
            created_billings.append(billing)

    sync_task_time_summary(task.pk)
    sync_task_billing_summary(task.pk)
    return created_billings

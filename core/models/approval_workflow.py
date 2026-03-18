from django.conf import settings
from django.db import models


class ApprovalWorkflow(models.Model):
    entity = models.ForeignKey(
        "ApprovalEntity",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column="entity_id",
    )
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(default=0)
    version = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    effective_from = models.DateTimeField(blank=True, null=True)
    effective_to = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "approval_workflows"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ApprovalWorkflowRule(models.Model):
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name="rules",
    )
    condition = models.ForeignKey(
        "ApprovalWorkflowCondition",
        on_delete=models.CASCADE,
        related_name="rules",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "id"]

    def __str__(self) -> str:
        return self.name


class ApprovalWorkflowCondition(models.Model):
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name="conditions",
    )
    field = models.CharField(max_length=255)
    operator = models.CharField(max_length=50)
    value = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.field} {self.operator} {self.value}".strip()


class WorkflowStep(models.Model):
    APPROVAL_TYPE_ALL = "ALL"
    APPROVAL_TYPE_ANY = "ANY"
    APPROVAL_TYPE_CHOICES = [
        (APPROVAL_TYPE_ALL, "All"),
        (APPROVAL_TYPE_ANY, "Any"),
    ]

    ESCALATION_TYPE_USER = "USER"
    ESCALATION_TYPE_ROLE = "ROLE"
    ESCALATION_TYPE_CHOICES = [
        (ESCALATION_TYPE_USER, "User"),
        (ESCALATION_TYPE_ROLE, "Role"),
    ]

    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name="steps",
        db_column="workflow_id",
    )
    step_order = models.PositiveIntegerField(default=1)
    step_name = models.CharField(max_length=255)
    approval_type = models.CharField(
        max_length=10,
        choices=APPROVAL_TYPE_CHOICES,
        default=APPROVAL_TYPE_ALL,
    )
    min_approvals_required = models.PositiveIntegerField(default=1)
    max_approvals_allowed = models.PositiveIntegerField(blank=True, null=True)
    is_parallel = models.BooleanField(default=False)
    allow_reject = models.BooleanField(default=True)
    allow_edit = models.BooleanField(default=False)
    allow_delegate = models.BooleanField(default=False)
    timeout_hours = models.PositiveIntegerField(blank=True, null=True)
    escalation_enabled = models.BooleanField(default=False)
    escalation_after_hours = models.PositiveIntegerField(blank=True, null=True)
    escalation_type = models.CharField(
        max_length=10,
        choices=ESCALATION_TYPE_CHOICES,
        blank=True,
    )
    escalation_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_step_escalations",
        db_column="escalation_user_id",
    )
    escalation_role_id = models.PositiveBigIntegerField(blank=True, null=True)
    is_final_step = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workflow_steps"
        ordering = ["step_order", "id"]
        unique_together = [("workflow", "step_order")]

    def __str__(self) -> str:
        return f"{self.workflow} - {self.step_name}"


class WorkflowStepApprover(models.Model):
    APPROVER_TYPE_USER = "USER"
    APPROVER_TYPE_ROLE = "ROLE"
    APPROVER_TYPE_DEPARTMENT = "DEPARTMENT"
    APPROVER_TYPE_DESIGNATION = "DESIGNATION"
    APPROVER_TYPE_CHOICES = [
        (APPROVER_TYPE_USER, "User"),
        (APPROVER_TYPE_ROLE, "Role"),
        (APPROVER_TYPE_DEPARTMENT, "Department"),
        (APPROVER_TYPE_DESIGNATION, "Designation"),
    ]

    step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        related_name="approvers",
        db_column="step_id",
    )
    approver_type = models.CharField(
        max_length=20,
        choices=APPROVER_TYPE_CHOICES,
        default=APPROVER_TYPE_USER,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_step_approvals",
        db_column="user_id",
    )
    role_id = models.PositiveBigIntegerField(blank=True, null=True)
    department = models.ForeignKey(
        "hr.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_step_approvals",
        db_column="department_id",
    )
    designation = models.ForeignKey(
        "hr.Designation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_step_approvals",
        db_column="designation_id",
    )
    sequence = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workflow_step_approvers"
        ordering = ["step", "sequence", "id"]

    def __str__(self) -> str:
        return f"{self.step} - {self.approver_type}"


class WorkflowStepCondition(models.Model):
    step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        related_name="conditions",
        db_column="step_id",
    )
    field_name = models.CharField(max_length=255)
    operator = models.CharField(max_length=50)
    value = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workflow_step_conditions"
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.step} - {self.field_name} {self.operator}".strip()


class ApprovalTransaction(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    entity = models.ForeignKey(
        "ApprovalEntity",
        on_delete=models.CASCADE,
        related_name="approval_transactions",
        db_column="entity_id",
    )
    record_id = models.CharField(max_length=255)
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.PROTECT,
        related_name="transactions",
        db_column="workflow_id",
    )
    current_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_transactions",
        db_column="current_step_id",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_approval_transactions",
    )
    submitted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "approval_transactions"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.entity} - {self.record_id}"


class ApprovalTransactionStep(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    transaction = models.ForeignKey(
        ApprovalTransaction,
        on_delete=models.CASCADE,
        related_name="steps",
        db_column="transaction_id",
    )
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.PROTECT,
        related_name="transaction_steps",
        db_column="workflow_step_id",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "approval_transaction_steps"
        ordering = ["transaction", "workflow_step__step_order", "id"]
        unique_together = [("transaction", "workflow_step")]

    def __str__(self) -> str:
        return f"{self.transaction} - {self.workflow_step}"


class ApprovalStepApprover(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_SKIPPED = "SKIPPED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_SKIPPED, "Skipped"),
    ]

    transaction_step = models.ForeignKey(
        ApprovalTransactionStep,
        on_delete=models.CASCADE,
        related_name="approvers",
        db_column="transaction_step_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_step_actions",
        db_column="user_id",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    is_required = models.BooleanField(default=True)
    acted_at = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "approval_step_approvers"
        ordering = ["transaction_step", "id"]
        unique_together = [("transaction_step", "user")]

    def __str__(self) -> str:
        return f"{self.transaction_step} - {self.user}"


class ApprovalAction(models.Model):
    ACTION_APPROVE = "APPROVE"
    ACTION_REJECT = "REJECT"
    ACTION_DELEGATE = "DELEGATE"
    ACTION_ESCALATE = "ESCALATE"
    ACTION_CHOICES = [
        (ACTION_APPROVE, "Approve"),
        (ACTION_REJECT, "Reject"),
        (ACTION_DELEGATE, "Delegate"),
        (ACTION_ESCALATE, "Escalate"),
    ]

    transaction = models.ForeignKey(
        ApprovalTransaction,
        on_delete=models.CASCADE,
        related_name="actions",
        db_column="transaction_id",
    )
    transaction_step = models.ForeignKey(
        ApprovalTransactionStep,
        on_delete=models.CASCADE,
        related_name="actions",
        db_column="transaction_step_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_actions",
        db_column="user_id",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    remarks = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    action_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "approval_actions"
        ordering = ["-action_at", "-id"]


class ApprovalDelegation(models.Model):
    delegator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_delegations_given",
        db_column="delegator_id",
    )
    delegate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_delegations_received",
        db_column="delegate_id",
    )
    entity = models.ForeignKey(
        "ApprovalEntity",
        on_delete=models.CASCADE,
        related_name="approval_delegations",
        db_column="entity_id",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "approval_delegations"
        ordering = ["-start_date", "-id"]


class ApprovalEscalation(models.Model):
    transaction_step = models.ForeignKey(
        ApprovalTransactionStep,
        on_delete=models.CASCADE,
        related_name="escalations",
        db_column="transaction_step_id",
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_escalations_from",
        db_column="from_user_id",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_escalations_to",
        db_column="to_user_id",
    )
    reason = models.TextField(blank=True)
    escalated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "approval_escalations"
        ordering = ["-escalated_at", "-id"]


class ApprovalAttachment(models.Model):
    transaction = models.ForeignKey(
        ApprovalTransaction,
        on_delete=models.CASCADE,
        related_name="attachments",
        db_column="transaction_id",
    )
    file = models.FileField(upload_to="approval_attachments/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_attachments_uploaded",
    )
    uploaded_at = models.DateTimeField()
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = "approval_attachments"
        ordering = ["-uploaded_at", "-id"]


class ApprovalNotification(models.Model):
    TYPE_SYSTEM = "SYSTEM"
    TYPE_EMAIL = "EMAIL"
    TYPE_SMS = "SMS"
    TYPE_CHOICES = [
        (TYPE_SYSTEM, "System"),
        (TYPE_EMAIL, "Email"),
        (TYPE_SMS, "SMS"),
    ]

    transaction = models.ForeignKey(
        ApprovalTransaction,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_column="transaction_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_notifications",
        db_column="user_id",
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_SYSTEM)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "approval_notifications"
        ordering = ["-created_at", "-id"]


class ApprovalAuditLog(models.Model):
    entity = models.ForeignKey(
        "ApprovalEntity",
        on_delete=models.CASCADE,
        related_name="approval_audit_logs",
        db_column="entity_id",
    )
    record_id = models.CharField(max_length=255)
    transaction = models.ForeignKey(
        ApprovalTransaction,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        db_column="transaction_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_audit_logs",
        db_column="user_id",
    )
    action = models.CharField(max_length=100)
    old_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "approval_audit_logs"
        ordering = ["-created_at", "-id"]

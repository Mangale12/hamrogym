from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_approvalworkflowrule_condition"),
        ("hr", "0012_leavetype_rename_leave_type_approvalworkflowlevel_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkflowStep",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("step_order", models.PositiveIntegerField(default=1)),
                ("step_name", models.CharField(max_length=255)),
                (
                    "approval_type",
                    models.CharField(
                        choices=[("ALL", "All"), ("ANY", "Any")],
                        default="ALL",
                        max_length=10,
                    ),
                ),
                ("min_approvals_required", models.PositiveIntegerField(default=1)),
                ("max_approvals_allowed", models.PositiveIntegerField(blank=True, null=True)),
                ("is_parallel", models.BooleanField(default=False)),
                ("allow_reject", models.BooleanField(default=True)),
                ("allow_edit", models.BooleanField(default=False)),
                ("allow_delegate", models.BooleanField(default=False)),
                ("timeout_hours", models.PositiveIntegerField(blank=True, null=True)),
                ("escalation_enabled", models.BooleanField(default=False)),
                ("escalation_after_hours", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "escalation_type",
                    models.CharField(
                        blank=True,
                        choices=[("USER", "User"), ("ROLE", "Role")],
                        max_length=10,
                    ),
                ),
                ("escalation_role_id", models.PositiveBigIntegerField(blank=True, null=True)),
                ("is_final_step", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "escalation_user",
                    models.ForeignKey(
                        blank=True,
                        db_column="escalation_user_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workflow_step_escalations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workflow",
                    models.ForeignKey(
                        db_column="workflow_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="steps",
                        to="core.approvalworkflow",
                    ),
                ),
            ],
            options={
                "db_table": "workflow_steps",
                "ordering": ["step_order", "id"],
                "unique_together": {("workflow", "step_order")},
            },
        ),
        migrations.CreateModel(
            name="ApprovalTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("record_id", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("IN_PROGRESS", "In Progress"),
                            ("APPROVED", "Approved"),
                            ("REJECTED", "Rejected"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "current_step",
                    models.ForeignKey(
                        blank=True,
                        db_column="current_step_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="current_transactions",
                        to="core.workflowstep",
                    ),
                ),
                (
                    "entity",
                    models.ForeignKey(
                        db_column="entity_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_transactions",
                        to="core.approvalentity",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="submitted_approval_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workflow",
                    models.ForeignKey(
                        db_column="workflow_id",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions",
                        to="core.approvalworkflow",
                    ),
                ),
            ],
            options={
                "db_table": "approval_transactions",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ApprovalAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="approval_attachments/")),
                ("uploaded_at", models.DateTimeField()),
                ("remarks", models.TextField(blank=True)),
                (
                    "transaction",
                    models.ForeignKey(
                        db_column="transaction_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="core.approvaltransaction",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approval_attachments_uploaded",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "approval_attachments",
                "ordering": ["-uploaded_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ApprovalAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("record_id", models.CharField(max_length=255)),
                ("action", models.CharField(max_length=100)),
                ("old_value", models.JSONField(blank=True, null=True)),
                ("new_value", models.JSONField(blank=True, null=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "entity",
                    models.ForeignKey(
                        db_column="entity_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_audit_logs",
                        to="core.approvalentity",
                    ),
                ),
                (
                    "transaction",
                    models.ForeignKey(
                        db_column="transaction_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="audit_logs",
                        to="core.approvaltransaction",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        db_column="user_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approval_audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "approval_audit_logs",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ApprovalDelegation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("reason", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "delegate",
                    models.ForeignKey(
                        db_column="delegate_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_delegations_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "delegator",
                    models.ForeignKey(
                        db_column="delegator_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_delegations_given",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "entity",
                    models.ForeignKey(
                        db_column="entity_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_delegations",
                        to="core.approvalentity",
                    ),
                ),
            ],
            options={
                "db_table": "approval_delegations",
                "ordering": ["-start_date", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ApprovalNotification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type",
                    models.CharField(
                        choices=[("SYSTEM", "System"), ("EMAIL", "Email"), ("SMS", "SMS")],
                        default="SYSTEM",
                        max_length=20,
                    ),
                ),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "transaction",
                    models.ForeignKey(
                        db_column="transaction_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="core.approvaltransaction",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "approval_notifications",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="WorkflowStepApprover",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "approver_type",
                    models.CharField(
                        choices=[
                            ("USER", "User"),
                            ("ROLE", "Role"),
                            ("DEPARTMENT", "Department"),
                            ("DESIGNATION", "Designation"),
                        ],
                        default="USER",
                        max_length=20,
                    ),
                ),
                ("role_id", models.PositiveBigIntegerField(blank=True, null=True)),
                ("sequence", models.PositiveIntegerField(default=1)),
                ("is_required", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "department",
                    models.ForeignKey(
                        blank=True,
                        db_column="department_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workflow_step_approvals",
                        to="hr.department",
                    ),
                ),
                (
                    "designation",
                    models.ForeignKey(
                        blank=True,
                        db_column="designation_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workflow_step_approvals",
                        to="hr.designation",
                    ),
                ),
                (
                    "step",
                    models.ForeignKey(
                        db_column="step_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approvers",
                        to="core.workflowstep",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        db_column="user_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workflow_step_approvals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "workflow_step_approvers",
                "ordering": ["step", "sequence", "id"],
            },
        ),
        migrations.CreateModel(
            name="WorkflowStepCondition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("field_name", models.CharField(max_length=255)),
                ("operator", models.CharField(max_length=50)),
                ("value", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "step",
                    models.ForeignKey(
                        db_column="step_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conditions",
                        to="core.workflowstep",
                    ),
                ),
            ],
            options={
                "db_table": "workflow_step_conditions",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="ApprovalTransactionStep",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("IN_PROGRESS", "In Progress"),
                            ("APPROVED", "Approved"),
                            ("REJECTED", "Rejected"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "transaction",
                    models.ForeignKey(
                        db_column="transaction_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="steps",
                        to="core.approvaltransaction",
                    ),
                ),
                (
                    "workflow_step",
                    models.ForeignKey(
                        db_column="workflow_step_id",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transaction_steps",
                        to="core.workflowstep",
                    ),
                ),
            ],
            options={
                "db_table": "approval_transaction_steps",
                "ordering": ["transaction", "workflow_step__step_order", "id"],
                "unique_together": {("transaction", "workflow_step")},
            },
        ),
        migrations.CreateModel(
            name="ApprovalStepApprover",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("APPROVED", "Approved"),
                            ("REJECTED", "Rejected"),
                            ("SKIPPED", "Skipped"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("is_required", models.BooleanField(default=True)),
                ("acted_at", models.DateTimeField(blank=True, null=True)),
                ("remarks", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "transaction_step",
                    models.ForeignKey(
                        db_column="transaction_step_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approvers",
                        to="core.approvaltransactionstep",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_step_actions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "approval_step_approvers",
                "ordering": ["transaction_step", "id"],
                "unique_together": {("transaction_step", "user")},
            },
        ),
        migrations.CreateModel(
            name="ApprovalAction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("APPROVE", "Approve"),
                            ("REJECT", "Reject"),
                            ("DELEGATE", "Delegate"),
                            ("ESCALATE", "Escalate"),
                        ],
                        max_length=20,
                    ),
                ),
                ("remarks", models.TextField(blank=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("action_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "transaction",
                    models.ForeignKey(
                        db_column="transaction_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="actions",
                        to="core.approvaltransaction",
                    ),
                ),
                (
                    "transaction_step",
                    models.ForeignKey(
                        db_column="transaction_step_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="actions",
                        to="core.approvaltransactionstep",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        db_column="user_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approval_actions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "approval_actions",
                "ordering": ["-action_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ApprovalEscalation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reason", models.TextField(blank=True)),
                ("escalated_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "from_user",
                    models.ForeignKey(
                        blank=True,
                        db_column="from_user_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approval_escalations_from",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "to_user",
                    models.ForeignKey(
                        blank=True,
                        db_column="to_user_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approval_escalations_to",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "transaction_step",
                    models.ForeignKey(
                        db_column="transaction_step_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="escalations",
                        to="core.approvaltransactionstep",
                    ),
                ),
            ],
            options={
                "db_table": "approval_escalations",
                "ordering": ["-escalated_at", "-id"],
            },
        ),
    ]

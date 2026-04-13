from django import forms

from ..models import ProjectEpic, Task, TaskBillableTo, TaskBillingStatus, TaskBillingType


class TaskForm(forms.ModelForm):
    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        if "code" in self.fields:
            self.fields["code"].required = False
            self.fields["code"].widget.attrs["readonly"] = True

        project_id = None
        if self.is_bound:
            raw_project_id = (self.data.get("project") or "").strip()
            project_id = int(raw_project_id) if raw_project_id.isdigit() else None
        elif self.instance and self.instance.project_id:
            project_id = self.instance.project_id

        if "epic" in self.fields:
            queryset = ProjectEpic.objects.select_related("project")
            if project_id:
                queryset = queryset.filter(project_id=project_id)
            self.fields["epic"].queryset = queryset.order_by("project__name", "name")

        if self.instance and self.instance.pk:
            for field_name in ["parent_task", "depends_on", "blocked_by"]:
                if field_name in self.fields:
                    self.fields[field_name].queryset = self.fields[field_name].queryset.exclude(pk=self.instance.pk)

    def clean(self):
        cleaned_data = super().clean()
        parent_task = cleaned_data.get("parent_task")
        depends_on = cleaned_data.get("depends_on")
        blocked_by = cleaned_data.get("blocked_by")
        project = cleaned_data.get("project")
        epic = cleaned_data.get("epic")
        module = cleaned_data.get("module")
        checklist_template = cleaned_data.get("checklist_template")
        is_blocked = cleaned_data.get("is_blocked")
        is_billable = cleaned_data.get("is_billable")

        if self.instance and self.instance.pk:
            if parent_task and parent_task.pk == self.instance.pk:
                self.add_error("parent_task", "A task cannot be its own parent.")

            if depends_on and depends_on.filter(pk=self.instance.pk).exists():
                self.add_error("depends_on", "A task cannot depend on itself.")

            if blocked_by and blocked_by.filter(pk=self.instance.pk).exists():
                self.add_error("blocked_by", "A task cannot be blocked by itself.")

        if parent_task and depends_on and depends_on.filter(pk=parent_task.pk).exists():
            self.add_error("depends_on", "Parent task does not need to be repeated in dependencies.")

        if depends_on and blocked_by:
            overlap_ids = set(depends_on.values_list("pk", flat=True)) & set(blocked_by.values_list("pk", flat=True))
            if overlap_ids:
                self.add_error("blocked_by", "The same task cannot appear in both Depends On and Blocked By.")

        if project and epic and epic.project_id != project.pk:
            self.add_error("epic", "Selected epic must belong to the chosen project.")

        if project and module and project.module_id and project.module_id != module.pk:
            self.add_error("module", "Selected module must match the project's module.")

        if not is_blocked:
            cleaned_data["blocked_reason"] = ""

        if not cleaned_data.get("require_approval"):
            cleaned_data["approved_by"] = None
            cleaned_data["approved_at"] = None

        if not is_billable:
            cleaned_data["billing_type"] = TaskBillingType.NONE
            cleaned_data["billing_status"] = TaskBillingStatus.NOT_BILLABLE
            cleaned_data["invoice_reference"] = ""
        elif cleaned_data.get("billing_status") == TaskBillingStatus.NOT_BILLABLE:
            cleaned_data["billing_status"] = TaskBillingStatus.UNBILLED

        if cleaned_data.get("billable_to") != TaskBillableTo.DEPARTMENT:
            cleaned_data["billable_department"] = None

        return cleaned_data

    class Meta:
        model = Task
        fields = [
            "code",
            "title",
            "description",
            "project",
            "epic",
            "module",
            "checklist_template",
            "task_type",
            "status",
            "team",
            "assignee",
            "parent_task",
            "labels",
            "depends_on",
            "blocked_by",
            "priority",
            "severity",
            "start_date",
            "due_date",
            "completed_at",
            "estimated_hours",
            "logged_hours",
            "is_billable",
            "billing_company_name",
            "billing_type",
            "rate_per_hour",
            "fixed_amount",
            "currency",
            "billable_to",
            "billable_department",
            "billing_status",
            "invoice_reference",
            "progress",
            "require_approval",
            "approved_by",
            "approved_at",
            "approval_status",
            "is_blocked",
            "blocked_reason",
            "is_active",
            "remarks",
        ]
        widgets = {
            "approved_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "completed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

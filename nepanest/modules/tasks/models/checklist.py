from django.db import models
from nepanest.common.mixins.erp import ERPBaseModel

class Checklist(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)
    project_id = models.ForeignKey("Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="checklists")
    module_id = models.ForeignKey("TaskModule", on_delete=models.SET_NULL, null=True, blank=True, related_name="checklists")

    class Meta:
        app_label = "task"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

class ChecklistItem(ERPBaseModel):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)

    class Meta:
        app_label = "task"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name

from django.conf import settings
from django.db import models

from core.choices import PRIORITY_CHOICES
from nepanest.common.mixins import ERPBaseModel


class ProjectStatus(models.TextChoices):
    PLANNED = "planned", "Planned"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    ON_HOLD = "on_hold", "On Hold"
    CANCELLED = "cancelled", "Cancelled"


class ProjectRole(models.TextChoices):
    OWNER = "owner", "Owner"
    MEMBER = "member", "Member"
    VIEWER = "viewer", "Viewer"


class Project(ERPBaseModel):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    module = models.ForeignKey("TaskModule", on_delete=models.RESTRICT, related_name="projects", null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PLANNED)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="managed_projects",
        null=True,
        blank=True,
    )

    class Meta:
        app_label = "task"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ProjectMember(ERPBaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_members")
    role = models.CharField(max_length=50, choices=ProjectRole.choices, default=ProjectRole.MEMBER)

    class Meta:
        app_label = "task"
        ordering = ["project__name", "user__username", "id"]
        constraints = [
            models.UniqueConstraint(fields=["project", "user"], name="unique_project_member"),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.project}"


class ProjectEpic(ERPBaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="epics")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PLANNED)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    progress = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "task"
        ordering = ["project__name", "name", "id"]

    def __str__(self) -> str:
        return self.name

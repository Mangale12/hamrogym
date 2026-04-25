from django.conf import settings
from django.db import models


class TeamRole(models.Model):
    organization = models.ForeignKey(
        "core.Organization", on_delete=models.PROTECT, null=True, blank=True
    )
    branch = models.ForeignKey(
        "core.Branch", on_delete=models.PROTECT, null=True, blank=True
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    level = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hr_team_roles_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "hr"
        ordering = ["level", "name"]
        verbose_name = "Team Role"
        verbose_name_plural = "Team Roles"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "name"],
                name="unique_team_role_name_per_branch",
            ),
        ]

    def __str__(self) -> str:
        return self.name

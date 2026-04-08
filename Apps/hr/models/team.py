from django.conf import settings
from django.db import models

from core.choices import TEAM_TYPE_CHOICES
from core.mixins import ERPBaseModel


class Team(ERPBaseModel):
    department = models.ForeignKey("Department", on_delete=models.PROTECT, null=True, blank=True, related_name="teams")
    parent_team = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="child_teams")
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="leading_teams")
    team_type = models.CharField(max_length=50, blank=True, choices=TEAM_TYPE_CHOICES)

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "branch", "name"],
                name="unique_team_name_per_branch",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class TeamMember(ERPBaseModel):
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="team_memberships")
    leader = models.BooleanField(default=False)
    role = models.ForeignKey("TeamRole", on_delete=models.PROTECT, null=True, blank=True, related_name="team_members")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ["team__name", "user__username", "-start_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["team", "user", "start_date"],
                name="unique_team_member_assignment_start",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.team}"

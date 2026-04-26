from django.db import models
from core.mixins import ERPBaseModel


class GymFacility(ERPBaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "branch"],
                name="unique_hamrogym_gym_facility_name_branch",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.branch.name}" if self.branch_id else self.name

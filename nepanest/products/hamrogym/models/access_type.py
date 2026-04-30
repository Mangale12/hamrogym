from django.db import models

from core.mixins import ERPBaseModel


class AccessType(ERPBaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "branch"],
                name="unique_hamrogym_access_type_name_branch",
            ),
            models.UniqueConstraint(
                fields=["code", "branch"],
                name="unique_hamrogym_access_type_code_branch",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.branch.name}" if self.branch_id else self.name

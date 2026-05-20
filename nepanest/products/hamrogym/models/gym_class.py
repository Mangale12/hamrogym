from django.db import models
from core.mixins.erp import ERPBaseModel
from nepanest.products.hamrogym.models.exercise import DIFFICULTY_LEVEL_CHOICES

class GymClass(ERPBaseModel):
    name = models.CharField(max_length=200)

    class_type = models.ForeignKey("GymClassType", on_delete=models.SET_NULL, null=True, blank=True, related_name="gym_classes")

    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVEL_CHOICES, default="Beginner")
    max_capacity = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField()
    trainer = models.ForeignKey("Trainer", on_delete=models.SET_NULL, null=True, blank=True, related_name="gym_classes")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

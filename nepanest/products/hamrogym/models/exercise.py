from django.db import models
from core.mixins.erp import ERPBaseModel

class Exercise(ERPBaseModel):
    
    EXERCISE_TYPE_CHOICES = [
        ('strength', 'Strength'),
        ('cardio', 'Cardio'),
        ('flexibility', 'Flexibility'),
    ]

    DIFFICULTY_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    muscle_group = models.ForeignKey("MuscleGroup", on_delete=models.SET_NULL, null=True, related_name="exercises")
    equipment_type = models.ForeignKey("EquipmentType", on_delete=models.SET_NULL, null=True, related_name="exercises")
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPE_CHOICES, null=True)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVEL_CHOICES, null=True)
    instructions = models.TextField(blank=True)
    precautions = models.TextField(blank=True)
    

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


# Expose class-level choices at module level for imports
DIFFICULTY_LEVEL_CHOICES = Exercise.DIFFICULTY_LEVEL_CHOICES

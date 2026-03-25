from django.db import models

from Apps.hr.models import Department,Shift


class Policy(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=255, unique=True)
    module = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=1)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Policy"
        verbose_name_plural = "Policies"

    def __str__(self) -> str:
        return self.name


class PolicyCondition(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="conditions")
    field_name = models.CharField(max_length=255)
    condition_value = models.TextField()
    operator = models.CharField(max_length=255)
    value = models.TextField()
    logical_operator = models.CharField(max_length=255)
    sequence = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["policy", "condition_type"]
        verbose_name = "Policy Condition"
        verbose_name_plural = "Policy Conditions"

    def __str__(self) -> str:
        return f"{self.policy.name} - {self.condition_type}"
    



class PolicyAction(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=255)
    action_value = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["policy", "action_type"]
        verbose_name = "Policy Action"
        verbose_name_plural = "Policy Actions"

    def __str__(self) -> str:
        return f"{self.policy.name} - {self.action_type}"
    

class PolicyScope(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="steps")
    scopeable = models.CharField(max_length=255)
    scopeable_id = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["policy", "step_order"]
        verbose_name = "Policy Step"
        verbose_name_plural = "Policy Steps"

    def __str__(self) -> str:
        return f"{self.policy.name} - {self.step_name}"
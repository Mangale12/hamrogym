from django.db import models
from core.choices import PRIORITY_CHOICES
from core.choices import PRIORITY_CHOICES
from core.mixins.erp import ERPBaseModel
from core.choices import PRIORITY_CHOICES

class Lead(ERPBaseModel):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    lead_source = models.ForeignKey("LeadSource", on_delete=models.SET_NULL, null=True, blank=True)
    lead_status = models.ForeignKey("LeadStatus", on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey("Service", on_delete=models.SET_NULL, null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    next_followup = models.DateTimeField(null=True, blank=True)
    party = models.ForeignKey("core.Party", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Inquiry(ERPBaseModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="inquiries")
    date = models.DateTimeField(null=True, blank=True)
    message = models.TextField()
    priority = models.CharField(max_length=50, null=True, blank=True, choices=PRIORITY_CHOICES)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Inquiry for {self.lead.name} - {self.subject}"
    
    
    
class FollowUp(ERPBaseModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="followups")
    followup_date = models.DateTimeField(null=True, blank=True)
    next_followup_date = models.DateTimeField(null=True, blank=True)
    discussion = models.TextField()
    is_completed = models.BooleanField(default=False)
    

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Follow-up for {self.lead.name} - {self.followup_date}"
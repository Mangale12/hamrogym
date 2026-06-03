from .lead_details import (
    LeadDetailView,
    LeadFollowUpCreateView,
    LeadFollowUpDeleteView,
    LeadFollowUpDetailView,
    LeadFollowUpUpdateView,
    LeadInquiryDetailView,
    LeadInquiryCreateView,
    LeadInquiryUpdateView,
    LeadModalDetailView,
    LeadModalUpdateView,
)
from .views import activity_list, company_list, contact_list, dashboard, deal_list, lead_list

__all__ = [
    "LeadDetailView",
    "LeadFollowUpCreateView",
    "LeadFollowUpDeleteView",
    "LeadFollowUpDetailView",
    "LeadFollowUpUpdateView",
    "LeadInquiryDetailView",
    "LeadInquiryCreateView",
    "LeadInquiryUpdateView",
    "LeadModalDetailView",
    "LeadModalUpdateView",
    "activity_list",
    "company_list",
    "contact_list",
    "dashboard",
    "deal_list",
    "lead_list",
]

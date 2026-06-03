from django.urls import path

from nepanest.modules.crm.views import (
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
    views,
)

urlpatterns = [
    path("dashboard/", views.dashboard, name="crm_dashboard"),
    path("leads/", views.lead_list, name="crm_lead_list"),
    path("leads/board/update-status/", views.lead_board_update_status, name="crm_lead_board_update_status"),
    path("leads/<int:pk>/view/", LeadDetailView.as_view(), name="crm_lead_view"),
    path("leads/<int:pk>/modal/detail/", LeadModalDetailView.as_view(), name="crm_lead_modal_detail"),
    path("leads/<int:pk>/modal/update/", LeadModalUpdateView.as_view(), name="crm_lead_modal_update"),
    path("leads/<int:pk>/inquiries/create/", LeadInquiryCreateView.as_view(), name="crm_lead_inquiry_create"),
    path("leads/<int:pk>/inquiries/<int:inquiry_pk>/detail/", LeadInquiryDetailView.as_view(), name="crm_lead_inquiry_detail"),
    path("leads/<int:pk>/inquiries/<int:inquiry_pk>/update/", LeadInquiryUpdateView.as_view(), name="crm_lead_inquiry_update"),
    path("leads/<int:pk>/followups/create/", LeadFollowUpCreateView.as_view(), name="crm_lead_followup_create"),
    path("leads/<int:pk>/followups/<int:followup_pk>/detail/", LeadFollowUpDetailView.as_view(), name="crm_lead_followup_detail"),
    path("leads/<int:pk>/followups/<int:followup_pk>/update/", LeadFollowUpUpdateView.as_view(), name="crm_lead_followup_update"),
    path("leads/<int:pk>/followups/<int:followup_pk>/delete/", LeadFollowUpDeleteView.as_view(), name="crm_lead_followup_delete"),
    path("contacts/", views.contact_list, name="crm_contact_list"),
    path("companies/", views.company_list, name="crm_company_list"),
    path("deals/", views.deal_list, name="crm_deal_list"),
    path("activities/", views.activity_list, name="crm_activity_list"),
]

from django.urls import path

from nepanest.modules.crm.views import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="crm_dashboard"),
    path("leads/", views.lead_list, name="crm_lead_list"),
    path("contacts/", views.contact_list, name="crm_contact_list"),
    path("companies/", views.company_list, name="crm_company_list"),
    path("deals/", views.deal_list, name="crm_deal_list"),
    path("activities/", views.activity_list, name="crm_activity_list"),
]

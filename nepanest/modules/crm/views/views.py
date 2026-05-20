from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse


def _crm_base_context():
    return {
        "stats": [
            {"label": "New Leads", "value": "128", "caption": "This month", "icon": "user-plus"},
            {"label": "Qualified Deals", "value": "36", "caption": "Active pipeline", "icon": "target"},
            {"label": "Follow Ups", "value": "18", "caption": "Due today", "icon": "clock"},
            {"label": "Won Revenue", "value": "$42k", "caption": "Quarter to date", "icon": "trending-up"},
        ],
        "quick_links": [
            {"label": "Leads", "url": reverse("crm_lead_list"), "icon": "user-plus"},
            {"label": "Contacts", "url": reverse("crm_contact_list"), "icon": "users"},
            {"label": "Companies", "url": reverse("crm_company_list"), "icon": "building"},
            {"label": "Deals", "url": reverse("crm_deal_list"), "icon": "target"},
        ],
        "pipeline": [
            {"stage": "New", "count": 24, "amount": "$12k"},
            {"stage": "Qualified", "count": 18, "amount": "$26k"},
            {"stage": "Proposal", "count": 11, "amount": "$31k"},
            {"stage": "Negotiation", "count": 7, "amount": "$19k"},
            {"stage": "Won", "count": 9, "amount": "$42k"},
        ],
    }


def _render_page(request, title, intro, items):
    context = {
        **_crm_base_context(),
        "page_title": title,
        "page_intro": intro,
        "records": items,
    }
    return render(request, "crm/module_page.html", context)


@login_required
def dashboard(request):
    context = {
        **_crm_base_context(),
        "page_title": "CRM Dashboard",
        "page_intro": "A focused CRM workspace for sales, follow-up, and pipeline visibility.",
        "focus_cards": [
            {
                "title": "Lead Intake",
                "description": "Capture prospects, inbound requests, and walk-in opportunities in one queue.",
                "icon": "inbox",
            },
            {
                "title": "Relationship Tracking",
                "description": "Keep contacts, companies, and touchpoints connected to every opportunity.",
                "icon": "users",
            },
            {
                "title": "Pipeline Control",
                "description": "Move deals through qualification, proposal, and close without switching products.",
                "icon": "target",
            },
        ],
    }
    return render(request, "crm/dashboard.html", context)


@login_required
def lead_list(request):
    return _render_page(
        request,
        "Leads",
        "Track new prospects before they become qualified opportunities.",
        [
            {"name": "Aarav Karki", "meta": "Website inquiry", "status": "New"},
            {"name": "Sajina Shrestha", "meta": "Referral campaign", "status": "Qualified"},
            {"name": "Northside Retail", "meta": "Cold outreach", "status": "Contacted"},
        ],
    )


@login_required
def contact_list(request):
    return _render_page(
        request,
        "Contacts",
        "Maintain the people behind every company, opportunity, and follow-up.",
        [
            {"name": "Nima Gurung", "meta": "Procurement Lead", "status": "Active"},
            {"name": "Rita Lama", "meta": "Operations Manager", "status": "Active"},
            {"name": "Prabesh KC", "meta": "Finance Reviewer", "status": "Nurturing"},
        ],
    )


@login_required
def company_list(request):
    return _render_page(
        request,
        "Companies",
        "Organize accounts and relationship ownership at the company level.",
        [
            {"name": "Everest Trade House", "meta": "Key account", "status": "Proposal"},
            {"name": "Summit Care", "meta": "Expansion target", "status": "Qualified"},
            {"name": "Urban Peak Labs", "meta": "Partner lead", "status": "Discovery"},
        ],
    )


@login_required
def deal_list(request):
    return _render_page(
        request,
        "Deals",
        "Monitor open opportunities, stage movement, and expected value.",
        [
            {"name": "Corporate Wellness Plan", "meta": "$8,500 expected", "status": "Negotiation"},
            {"name": "Annual Membership Bundle", "meta": "$3,200 expected", "status": "Proposal"},
            {"name": "Team Training Contract", "meta": "$12,000 expected", "status": "Qualified"},
        ],
    )


@login_required
def activity_list(request):
    return _render_page(
        request,
        "Activities",
        "Keep calls, meetings, and reminders visible for the whole CRM team.",
        [
            {"name": "Follow-up call with Everest Trade House", "meta": "Today, 2:30 PM", "status": "Scheduled"},
            {"name": "Proposal review with Summit Care", "meta": "Tomorrow, 11:00 AM", "status": "Upcoming"},
            {"name": "Renewal reminder for Urban Peak Labs", "meta": "Friday, 9:00 AM", "status": "Pending"},
        ],
    )

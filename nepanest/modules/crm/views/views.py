from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from nepanest.modules.crm.models import Lead, LeadStatus


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
    leads = list(
        Lead.objects.select_related("lead_status", "assigned_to", "service", "lead_source")
        .order_by("lead_status__sequence", "name")
    )
    statuses = list(LeadStatus.objects.order_by("sequence", "name", "id"))
    default_status = next((status for status in statuses if status.is_default), statuses[0] if statuses else None)
    grouped = defaultdict(list)

    total_budget = 0
    converted_budget = 0
    age_days = []

    for lead in leads:
        status = lead.lead_status or default_status
        if not status:
            continue
        grouped[status.pk].append(
            {
                "id": lead.pk,
                "name": lead.name,
                "phone": lead.phone or "No phone",
                "email": lead.email or "No email",
                "company_name": lead.company_name or "Independent",
                "service_name": lead.service.name if lead.service else "General",
                "assigned_to": (
                    lead.assigned_to.get_full_name() or lead.assigned_to.username
                    if lead.assigned_to
                    else "Unassigned"
                ),
                "budget": lead.budget or 0,
                "next_followup": timezone.localtime(lead.next_followup).strftime("%b %d, %I:%M %p")
                if lead.next_followup
                else "Not scheduled",
                "next_followup_value": timezone.localtime(lead.next_followup).strftime("%Y-%m-%dT%H:%M:%S")
                if lead.next_followup
                else "",
                "status_id": status.pk,
                "detail_url": reverse("crm_lead_view", kwargs={"pk": lead.pk}),
            }
        )
        total_budget += float(lead.budget or 0)
        if status.is_closed:
            converted_budget += float(lead.budget or 0)
        if lead.created_at:
            age_days.append(max((timezone.localtime().date() - timezone.localtime(lead.created_at).date()).days, 0))

    columns = [
        {
            "status": status,
            "leads": grouped.get(status.pk, []),
            "count": len(grouped.get(status.pk, [])),
            "value": sum(float(item["budget"]) for item in grouped.get(status.pk, [])),
        }
        for status in statuses
    ]

    total_leads = len(leads)
    converted_leads = sum(len(column["leads"]) for column in columns if column["status"].is_closed)
    context = {
        **_crm_base_context(),
        "page_title": "Lead Board",
        "page_intro": "Drag leads between columns to update status and click any lead to schedule a followup.",
        "columns": columns,
        "board_summary": {
            "total_leads": total_leads,
            "total_value": total_budget,
            "conversion_rate": round((converted_leads / total_leads) * 100, 2) if total_leads else 0,
            "won_value": converted_budget,
            "avg_lead_age": round(sum(age_days) / len(age_days), 1) if age_days else 0,
        },
        "followup_modal_fields": [
            {
                "name": "lead_name",
                "label": "Lead",
                "type": "text",
                "value": "",
                "attributes": {"readonly": "readonly"},
                "col": 6,
            },
            {
                "name": "followup_date",
                "label": "Followup Date",
                "type": "datetime",
                "value": timezone.localtime().strftime("%Y-%m-%dT%H:%M:%S"),
                "required": True,
                "col": 6,
            },
            {
                "name": "next_followup_date",
                "label": "Next Followup",
                "type": "datetime",
                "value": "",
                "col": 6,
            },
            {
                "name": "is_completed",
                "label": "Completed",
                "type": "checkbox",
                "default": False,
                "col": 6,
            },
            {
                "name": "discussion",
                "label": "Discussion",
                "type": "textarea",
                "placeholder": "What happened in this followup?",
                "required": True,
                "col": 12,
            },
        ],
    }
    return render(request, "crm/lead_board.html", context)


@login_required
def lead_board_update_status(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    lead_id = (request.POST.get("lead_id") or "").strip()
    status_id = (request.POST.get("status_id") or "").strip()
    if not lead_id.isdigit() or not status_id.isdigit():
        return JsonResponse({"success": False, "message": "Lead and status are required."}, status=400)

    lead = get_object_or_404(Lead, pk=int(lead_id))
    status = get_object_or_404(LeadStatus, pk=int(status_id))
    lead.lead_status = status
    lead.save(update_fields=["lead_status"])
    return JsonResponse({"success": True, "message": "Lead status updated successfully."})


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

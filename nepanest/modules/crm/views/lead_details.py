import calendar
from collections import Counter, defaultdict
from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View

from nepanest.modules.crm.forms.lead_form import FollowUpForm, InquiryForm, LeadForm
from core.choices import PRIORITY_CHOICES
from nepanest.modules.crm.models import FollowUp, Inquiry, Lead, LeadSource, LeadStatus, Service


def _serialize_form_errors(form):
    errors = {}
    for field, field_errors in form.errors.items():
        errors[field] = [str(error) for error in field_errors]
    return errors


def _datetime_local_value(value):
    if not value:
        return ""
    local_value = timezone.localtime(value) if timezone.is_aware(value) else value
    return local_value.strftime("%Y-%m-%dT%H:%M:%S")


def _sync_lead_followup_state(lead):
    latest_followup = (
        FollowUp.objects.filter(lead=lead)
        .order_by("-followup_date", "-created_at")
        .first()
    )
    lead.last_contacted = (
        latest_followup.followup_date if latest_followup and latest_followup.followup_date else lead.last_contacted
    )
    lead.next_followup = latest_followup.next_followup_date if latest_followup else None
    lead.save(update_fields=["last_contacted", "next_followup"])


class LeadModalForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "name",
            "email",
            "phone",
            "company_name",
            "lead_source",
            "lead_status",
            "assigned_to",
            "service",
            "budget",
            "next_followup",
        ]


class LeadDetailView(LoginRequiredMixin, View):
    template_name = "crm/lead/show.html"
    partial_template_name = "crm/lead/partials/detail_content.html"

    def get(self, request, pk):
        lead = get_object_or_404(
            Lead.objects.select_related(
                "lead_source",
                "lead_status",
                "assigned_to",
                "service",
                "party",
            ),
            pk=pk,
        )
        context = self._build_context_data(lead)
        if request.GET.get("fragment") == "detail":
            return render(request, self.partial_template_name, context)
        return render(request, self.template_name, context)

    def _build_context_data(self, lead):
        inquiries = list(
            Inquiry.objects.filter(lead=lead).order_by("-date", "-created_at")
        )
        followups = list(
            FollowUp.objects.filter(lead=lead).order_by("-followup_date", "-created_at")
        )
        now = timezone.localtime()
        lead_created = timezone.localtime(lead.created_at) if lead.created_at else now
        lead_age_days = max((now.date() - lead_created.date()).days, 0)

        upcoming_followups = [
            item
            for item in followups
            if item.next_followup_date
            and timezone.localtime(item.next_followup_date) >= now
            and not item.is_completed
        ]
        completed_followups = [item for item in followups if item.is_completed]
        missed_followups = [
            item
            for item in followups
            if item.followup_date
            and timezone.localtime(item.followup_date) < now
            and not item.is_completed
        ]

        timeline_items = self._build_timeline_items(lead, inquiries, followups, now)
        inquiry_summary = self._build_inquiry_summary(inquiries)
        followup_summary = self._build_followup_summary(
            followups, upcoming_followups, completed_followups, missed_followups
        )
        calendar_weeks = self._build_followup_calendar(followups, lead.next_followup, now)
        activity_chart = self._build_activity_chart(timeline_items)
        tags = self._build_tags(lead, inquiries)

        context = {
            "lead": lead,
            "lead_initials": self._lead_initials(lead.name),
            "lead_age_days": lead_age_days,
            "lead_age_label": f"{lead_age_days} day{'s' if lead_age_days != 1 else ''}",
            "inquiries": inquiries,
            "followups": followups,
            "upcoming_followups": upcoming_followups,
            "completed_followups": completed_followups,
            "missed_followups": missed_followups,
            "timeline_items": timeline_items,
            "activity_chart": activity_chart,
            "calendar_weeks": calendar_weeks,
            "calendar_month_label": calendar_weeks["month_label"],
            "lead_tags": tags,
            "summary_cards": [
                {
                    "label": "Inquiries",
                    "value": len(inquiries),
                    "note": "Messages and requests logged for this lead.",
                },
                {
                    "label": "Follow-ups",
                    "value": len(followups),
                    "note": "All touchpoints recorded by the team.",
                },
                {
                    "label": "Upcoming",
                    "value": len(upcoming_followups),
                    "note": "Pending next actions still waiting on the team.",
                },
                {
                    "label": "Completed",
                    "value": len(completed_followups),
                    "note": "Follow-ups already resolved and marked complete.",
                },
            ],
            "tab_counts": {
                "overview": 0,
                "inquiries": len(inquiries),
                "followups": len(followups),
                "tasks": 0,
                "notes": max(1, min(len(timeline_items), 3)) if timeline_items else 0,
                "files": 0,
                "activity": len(timeline_items),
            },
            "lead_badges": [
                {
                    "label": lead.lead_status.name if lead.lead_status else "New",
                    "tone": "blue",
                },
                {
                    "label": lead.lead_source.name if lead.lead_source else "Direct",
                    "tone": "violet",
                },
                {
                    "label": lead.service.name if lead.service else "Gym Membership",
                    "tone": "green",
                },
                {
                    "label": self._priority_from_inquiries(inquiries),
                    "tone": "red",
                },
            ],
            "lead_meta_rows": [
                {
                    "label": "Assigned To",
                    "value": self._user_label(lead.assigned_to),
                    "icon": "user",
                },
                {
                    "label": "Next Followup",
                    "value": self._format_dt(lead.next_followup),
                    "icon": "calendar",
                },
                {
                    "label": "Last Contacted",
                    "value": self._format_dt(lead.last_contacted),
                    "icon": "clock",
                },
                {
                    "label": "Lead Age",
                    "value": f"{lead_age_days} days",
                    "icon": "activity",
                },
                {
                    "label": "Lead Status",
                    "value": lead.lead_status.name if lead.lead_status else "New",
                    "icon": "flag",
                },
                {
                    "label": "Lead Source",
                    "value": lead.lead_source.name if lead.lead_source else "Direct",
                    "icon": "globe",
                },
                {
                    "label": "Service",
                    "value": lead.service.name if lead.service else "Gym Membership",
                    "icon": "briefcase",
                },
                {
                    "label": "Budget",
                    "value": self._format_budget(lead.budget),
                    "icon": "credit-card",
                },
            ],
            "lead_information_rows": [
                ("Lead Status", lead.lead_status.name if lead.lead_status else "New"),
                ("Lead Source", lead.lead_source.name if lead.lead_source else "Direct"),
                ("Service Interested", lead.service.name if lead.service else "Gym Membership"),
                ("Budget", self._format_budget(lead.budget)),
                ("Company", lead.company_name or "Not provided"),
                ("Email", lead.email or "Not provided"),
                ("Phone", lead.phone or "Not provided"),
                ("Linked Party", lead.party.name if lead.party else "Not converted"),
                ("Description", self._lead_description(lead, inquiries)),
            ],
            "inquiry_summary": inquiry_summary,
            "followup_summary": followup_summary,
            "notes_preview": self._notes_preview(lead, timeline_items),
            "now": now,
            "lead_edit_attrs": {
                "data-bs-toggle": "modal",
                "data-bs-target": "#leadEditModal",
            },
            "inquiry_modal_attrs": {
                "data-bs-toggle": "modal",
                "data-bs-target": "#inquiryModal",
            },
            "followup_modal_attrs": {
                "data-bs-toggle": "modal",
                "data-bs-target": "#followupModal",
            },
            "inquiry_filter_fields": [
                {
                    "name": "search",
                    "label": "Search",
                    "type": "text",
                    "placeholder": "Search inquiries...",
                    "col": 4,
                },
                {
                    "name": "priority",
                    "label": "Priority",
                    "type": "static_select",
                    "options": PRIORITY_CHOICES,
                    "col": 3,
                },
                {
                    "name": "source",
                    "label": "Source",
                    "type": "static_select",
                    "options": self._modal_choice_options(LeadSource.objects.order_by("name"), "name"),
                    "col": 2,
                },
                {
                    "name": "date_range",
                    "label": "Date Range",
                    "type": "text",
                    "placeholder": "Select date range",
                    "col": 3,
                },
            ],
            "followup_filter_fields": [
                {
                    "name": "followup_status",
                    "label": "Followup Status",
                    "type": "static_select",
                    "options": [
                        ("upcoming", "Upcoming"),
                        ("completed", "Completed"),
                        ("missed", "Missed"),
                    ],
                    "col": 4,
                },
                {
                    "name": "followup_date_range",
                    "label": "Date Range",
                    "type": "text",
                    "placeholder": "Select date range",
                    "col": 4,
                },
            ],
            "lead_modal_fields": self._lead_modal_fields(lead),
            "inquiry_modal_fields": self._inquiry_modal_fields(lead),
            "followup_modal_fields": self._followup_modal_fields(lead),
        }
        return context

    def _lead_initials(self, name):
        parts = [part[:1].upper() for part in (name or "").split()[:2] if part]
        return "".join(parts) or "LD"

    def _format_dt(self, value):
        if not value:
            return "Not scheduled"
        return timezone.localtime(value).strftime("%b %d, %Y  %I:%M %p")

    def _format_budget(self, budget):
        if budget in (None, ""):
            return "Not set"
        return f"Rs. {budget:,.0f}"

    def _user_label(self, user):
        if not user:
            return "Unassigned"
        full_name = user.get_full_name()
        return full_name or user.username

    def _priority_from_inquiries(self, inquiries):
        weights = {"high": 3, "medium": 2, "low": 1}
        best = "low"
        for inquiry in inquiries:
            if weights.get(inquiry.priority or "", 0) > weights.get(best, 0):
                best = inquiry.priority
        return {
            "high": "High Priority",
            "medium": "Medium Priority",
            "low": "Low Priority",
        }.get(best, "Normal Priority")

    def _lead_description(self, lead, inquiries):
        if inquiries:
            return inquiries[0].message[:110]
        if lead.service:
            return f"Interested in {lead.service.name.lower()} and currently in the CRM pipeline."
        return "Lead is in the CRM pipeline and ready for follow-up."

    def _topic_from_subject(self, subject):
        lowered = (subject or "").lower()
        if "trainer" in lowered:
            return "Trainer"
        if "price" in lowered or "pricing" in lowered or "discount" in lowered:
            return "Pricing"
        if "class" in lowered:
            return "Classes"
        if "diet" in lowered:
            return "Nutrition"
        if "membership" in lowered:
            return "Membership"
        return "General"

    def _source_for_inquiry(self, lead, inquiry):
        source_name = (lead.lead_source.name if lead.lead_source else "").lower()
        message = (inquiry.message or "").lower()
        if "phone" in message or "call" in message:
            return "Phone Call"
        if "whatsapp" in message:
            return "WhatsApp"
        if "website" in source_name:
            return "Website"
        if "facebook" in source_name or "instagram" in source_name:
            return "Social"
        return lead.lead_source.name if lead.lead_source else "Website"

    def _channel_for_inquiry(self, inquiry):
        subject = (inquiry.subject or "").lower()
        message = (inquiry.message or "").lower()
        if "call" in subject or "call" in message or "phone" in message:
            return "Call"
        if "form" in subject or "website" in message:
            return "Web Form"
        return "Email"

    def _inquiry_icon(self, inquiry):
        channel = self._channel_for_inquiry(inquiry).lower()
        if "call" in channel:
            return "phone"
        if "web" in channel:
            return "globe"
        return "message-circle"

    def _followup_status(self, followup, now):
        if followup.is_completed:
            return "completed"
        if followup.followup_date and timezone.localtime(followup.followup_date) < now:
            return "missed"
        return "upcoming"

    def _build_timeline_items(self, lead, inquiries, followups, now):
        items = []
        for inquiry in inquiries:
            occurred_at = inquiry.date or inquiry.created_at
            items.append(
                {
                    "kind": "inquiry",
                    "title": inquiry.subject,
                    "copy": inquiry.message,
                    "when": occurred_at,
                    "date_label": self._format_dt(occurred_at),
                    "author": "By " + self._user_label(getattr(inquiry, "created_by", None) or lead.assigned_to),
                    "icon": self._inquiry_icon(inquiry),
                    "accent": inquiry.priority or "low",
                    "status_label": inquiry.get_priority_display() if inquiry.priority else "Open",
                    "source": self._source_for_inquiry(lead, inquiry),
                    "channel": self._channel_for_inquiry(inquiry),
                    "priority": inquiry.get_priority_display() if inquiry.priority else "Low",
                }
            )

        for followup in followups:
            occurred_at = followup.followup_date or followup.created_at
            status = self._followup_status(followup, now)
            items.append(
                {
                    "kind": "followup",
                    "title": "Follow-up discussion",
                    "copy": followup.discussion,
                    "when": occurred_at,
                    "date_label": self._format_dt(occurred_at),
                    "author": "Assigned to " + self._user_label(getattr(followup, "created_by", None) or lead.assigned_to),
                    "icon": "calendar-check" if status == "completed" else "calendar",
                    "accent": status,
                    "status_label": status.title(),
                    "next_label": self._format_dt(followup.next_followup_date),
                    "mode": "Call",
                    "is_completed": followup.is_completed,
                }
            )

        items.sort(
            key=lambda item: timezone.localtime(item["when"]) if item["when"] else now,
            reverse=True,
        )
        return items

    def _build_inquiry_summary(self, inquiries):
        counts = Counter((inquiry.priority or "low") for inquiry in inquiries)
        return {
            "total": len(inquiries),
            "high": counts.get("high", 0),
            "medium": counts.get("medium", 0),
            "low": counts.get("low", 0),
            "open": len(inquiries),
            "closed": 0,
        }

    def _build_followup_summary(self, followups, upcoming_followups, completed_followups, missed_followups):
        return {
            "total": len(followups),
            "upcoming": len(upcoming_followups),
            "completed": len(completed_followups),
            "missed": len(missed_followups),
        }

    def _build_activity_chart(self, timeline_items):
        daily_counts = defaultdict(int)
        for item in timeline_items:
            if item["when"]:
                daily_counts[timezone.localtime(item["when"]).date()] += 1

        if not daily_counts:
            return []

        latest_days = sorted(daily_counts.keys())[-6:]
        max_count = max(daily_counts[day] for day in latest_days) or 1
        return [
            {
                "label": day.strftime("%d %b"),
                "count": daily_counts[day],
                "height": max(16, int((daily_counts[day] / max_count) * 100)),
            }
            for day in latest_days
        ]

    def _build_followup_calendar(self, followups, focus_date, now):
        basis = timezone.localtime(focus_date) if focus_date else now
        year = basis.year
        month = basis.month
        month_days = calendar.Calendar(firstweekday=6).monthdatescalendar(year, month)

        followup_map = defaultdict(list)
        for followup in followups:
            if followup.followup_date:
                followup_map[timezone.localtime(followup.followup_date).date()].append(followup)

        weeks = []
        for week in month_days:
            week_cells = []
            for day in week:
                day_followups = followup_map.get(day, [])
                status = ""
                if day_followups:
                    if any(item.is_completed for item in day_followups):
                        status = "completed"
                    elif any(
                        timezone.localtime(item.followup_date) < now and not item.is_completed
                        for item in day_followups
                        if item.followup_date
                    ):
                        status = "missed"
                    else:
                        status = "upcoming"
                week_cells.append(
                    {
                        "day": day.day,
                        "in_month": day.month == month,
                        "is_today": day == now.date(),
                        "count": len(day_followups),
                        "status": status,
                    }
                )
            weeks.append(week_cells)

        return {
            "month_label": basis.strftime("%B %Y"),
            "weeks": weeks,
            "weekdays": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        }

    def _build_tags(self, lead, inquiries):
        tags = []
        if lead.service:
            tags.append(lead.service.name)
        if lead.lead_source:
            tags.append(lead.lead_source.name)
        if lead.company_name:
            tags.append("Corporate")
        topics = []
        for inquiry in inquiries[:4]:
            topic = self._topic_from_subject(inquiry.subject)
            if topic not in topics:
                topics.append(topic)
        tags.extend(topics)
        return tags[:6] or ["Interested"]

    def _notes_preview(self, lead, timeline_items):
        preview = []
        if timeline_items:
            preview.append(timeline_items[0]["copy"][:120])
        if lead.company_name:
            preview.append(f"Company linked: {lead.company_name}.")
        if lead.next_followup:
            preview.append(
                f"Next follow-up planned for {self._format_dt(lead.next_followup)}."
            )
        return preview[:3]

    def _modal_choice_options(self, queryset, field_name):
        return [(str(obj.pk), getattr(obj, field_name)) for obj in queryset]

    def _lead_modal_fields(self, lead):
        User = get_user_model()
        return [
            {"name": "name", "label": "Lead Name", "type": "text", "value": lead.name, "required": True, "col": 6},
            {"name": "email", "label": "Email", "type": "email", "value": lead.email, "col": 6},
            {"name": "phone", "label": "Phone", "type": "text", "value": lead.phone, "col": 4},
            {"name": "company_name", "label": "Company", "type": "text", "value": lead.company_name, "col": 4},
            {
                "name": "budget",
                "label": "Budget",
                "type": "number",
                "value": lead.budget,
                "prefix": "Rs.",
                "col": 4,
            },
            {
                "name": "lead_source",
                "label": "Lead Source",
                "type": "static_select",
                "value": str(lead.lead_source_id or ""),
                "options": self._modal_choice_options(LeadSource.objects.order_by("name"), "name"),
                "col": 4,
            },
            {
                "name": "lead_status",
                "label": "Lead Status",
                "type": "static_select",
                "value": str(lead.lead_status_id or ""),
                "options": self._modal_choice_options(LeadStatus.objects.order_by("name"), "name"),
                "col": 4,
            },
            {
                "name": "service",
                "label": "Service",
                "type": "static_select",
                "value": str(lead.service_id or ""),
                "options": self._modal_choice_options(Service.objects.order_by("name"), "name"),
                "col": 4,
            },
            {
                "name": "assigned_to",
                "label": "Assigned To",
                "type": "static_select",
                "value": str(lead.assigned_to_id or ""),
                "options": [
                    (str(user.pk), user.get_full_name() or user.username)
                    for user in User.objects.order_by("first_name", "username")
                ],
                "col": 6,
            },
            {
                "name": "next_followup",
                "label": "Next Followup",
                "type": "datetime",
                "value": _datetime_local_value(lead.next_followup),
                "col": 6,
            },
        ]

    def _inquiry_modal_fields(self, lead):
        return [
            {
                "name": "lead_name",
                "label": "Lead",
                "type": "text",
                "value": lead.name,
                "attributes": {"readonly": "readonly"},
                "col": 6,
            },
            {
                "name": "date",
                "label": "Inquiry Date",
                "type": "datetime",
                "value": _datetime_local_value(timezone.localtime()),
                "col": 6,
            },
            {
                "name": "subject",
                "label": "Subject",
                "type": "text",
                "placeholder": "Inquiry subject",
                "required": True,
                "col": 8,
            },
            {
                "name": "priority",
                "label": "Priority",
                "type": "static_select",
                "options": PRIORITY_CHOICES,
                "required": True,
                "col": 4,
            },
            {
                "name": "message",
                "label": "Message",
                "type": "textarea",
                "placeholder": "Add inquiry details",
                "required": True,
                "col": 12,
            },
            {
                "name": "attachment",
                "label": "Attachment",
                "type": "file",
                "col": 12,
            },
        ]

    def _followup_modal_fields(self, lead):
        return [
            {
                "name": "lead_name",
                "label": "Lead",
                "type": "text",
                "value": lead.name,
                "attributes": {"readonly": "readonly"},
                "col": 6,
            },
            {
                "name": "followup_date",
                "label": "Followup Date",
                "type": "datetime",
                "value": _datetime_local_value(timezone.localtime()),
                "required": True,
                "col": 6,
            },
            {
                "name": "next_followup_date",
                "label": "Next Followup",
                "type": "datetime",
                "value": _datetime_local_value(lead.next_followup),
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
        ]


class LeadModalDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk)
        return JsonResponse(
            {
                "data": {
                    "id": lead.pk,
                    "name": lead.name,
                    "email": lead.email or "",
                    "phone": lead.phone or "",
                    "company_name": lead.company_name or "",
                    "budget": lead.budget or "",
                    "lead_source": str(lead.lead_source_id or ""),
                    "lead_status": str(lead.lead_status_id or ""),
                    "service": str(lead.service_id or ""),
                    "assigned_to": str(lead.assigned_to_id or ""),
                    "next_followup": _datetime_local_value(lead.next_followup),
                    "last_contacted": _datetime_local_value(lead.last_contacted),
                    "party": str(lead.party_id or ""),
                }
            }
        )


class LeadModalUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk)
        form = LeadModalForm(request.POST, instance=lead)
        if not form.is_valid():
            return JsonResponse({"errors": _serialize_form_errors(form)}, status=400)

        form.save()
        return JsonResponse({"success": True, "id": lead.pk})


class LeadInquiryCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk)
        payload = request.POST.copy()
        payload["lead"] = str(lead.pk)
        form = InquiryForm(payload, request.FILES)
        if not form.is_valid():
            return JsonResponse({"errors": _serialize_form_errors(form)}, status=400)

        inquiry = form.save()
        if inquiry.date:
            lead.last_contacted = inquiry.date
            lead.save(update_fields=["last_contacted"])
        return JsonResponse({"success": True, "id": inquiry.pk})


class LeadInquiryDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, inquiry_pk):
        inquiry = get_object_or_404(Inquiry, pk=inquiry_pk, lead_id=pk)
        return JsonResponse(
            {
                "data": {
                    "id": inquiry.pk,
                    "lead_name": inquiry.lead.name,
                    "date": _datetime_local_value(inquiry.date),
                    "subject": inquiry.subject,
                    "priority": inquiry.priority or "",
                    "message": inquiry.message,
                }
            }
        )


class LeadInquiryUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, inquiry_pk):
        inquiry = get_object_or_404(Inquiry, pk=inquiry_pk, lead_id=pk)
        payload = request.POST.copy()
        payload["lead"] = str(pk)
        form = InquiryForm(payload, request.FILES, instance=inquiry)
        if not form.is_valid():
            return JsonResponse({"errors": _serialize_form_errors(form)}, status=400)

        inquiry = form.save()
        if inquiry.date:
            inquiry.lead.last_contacted = inquiry.date
            inquiry.lead.save(update_fields=["last_contacted"])
        return JsonResponse({"success": True, "id": inquiry.pk})


class LeadFollowUpCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk)
        payload = request.POST.copy()
        payload["lead"] = str(lead.pk)
        form = FollowUpForm(payload)
        if not form.is_valid():
            return JsonResponse({"errors": _serialize_form_errors(form)}, status=400)

        followup = form.save()
        _sync_lead_followup_state(lead)
        return JsonResponse({"success": True, "id": followup.pk})


class LeadFollowUpDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, followup_pk):
        followup = get_object_or_404(FollowUp, pk=followup_pk, lead_id=pk)
        return JsonResponse(
            {
                "data": {
                    "id": followup.pk,
                    "lead_name": followup.lead.name,
                    "followup_date": _datetime_local_value(followup.followup_date),
                    "next_followup_date": _datetime_local_value(followup.next_followup_date),
                    "is_completed": followup.is_completed,
                    "discussion": followup.discussion,
                }
            }
        )


class LeadFollowUpUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk, followup_pk):
        followup = get_object_or_404(FollowUp, pk=followup_pk, lead_id=pk, is_completed=False)
        payload = request.POST.copy()
        payload["lead"] = str(pk)
        form = FollowUpForm(payload, instance=followup)
        if not form.is_valid():
            return JsonResponse({"errors": _serialize_form_errors(form)}, status=400)

        followup = form.save()
        _sync_lead_followup_state(followup.lead)
        return JsonResponse({"success": True, "id": followup.pk})


class LeadFollowUpDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, followup_pk):
        followup = get_object_or_404(FollowUp, pk=followup_pk, lead_id=pk, is_completed=False)
        lead = followup.lead
        followup.delete()
        _sync_lead_followup_state(lead)
        return JsonResponse({"success": True, "message": "Followup deleted successfully."})

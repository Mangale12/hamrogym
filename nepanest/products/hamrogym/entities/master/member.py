from core.config import EntityConfig
from core.registry import register_entity
from nepanest.common.helpers.helper import encode_date_for_display
from nepanest.common.utils.dynamic_sections import parse_dynamic_section

from ...datatables.member_data_table import MEMBER_COLUMNS, MemberDataTableView
from ...forms.member_form import MemberForm
from core.models import PartyIndividualProfile

from ...models import FitnessGoal, Member, MemberMembership, MembershipExtension, MembershipFreeze, MembershipUpgrade


MEMBERSHIP_SECTION = {
    "title": "Memberships",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "membership_plan", "label": "Plan", "type": "select", "required": True, "url_name": "membership_plan_select"},
        {"name": "start_date", "label": "Start Date", "type": "date", "required": True},
        {"name": "end_date", "label": "End Date", "type": "date", "required": True},
        {"name": "total_sessions", "label": "Total Sessions", "type": "number", "required": False, "min": 0},
        {"name": "used_sessions", "label": "Used Sessions", "type": "number", "required": False, "min": 0},
        {"name": "remaining_sessions", "label": "Remaining", "type": "number", "required": False, "min": 0, "readonly": True},
        {"name": "status", "label": "Status", "type": "static_select", "required": True, "options": [("", "Select Status"), *MemberMembership.Status.choices]},
        {"name": "source", "label": "Source", "type": "static_select", "required": True, "options": [("", "Select Source"), *MemberMembership.Source.choices]},
        {"name": "notes", "label": "Notes", "type": "textarea", "required": False},
    ],
}

FREEZE_SECTION = {
    "title": "Freezes",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "membership", "label": "Membership", "type": "select", "required": True, "url_name": "member_membership_select"},
        {"name": "start_date", "label": "Start Date", "type": "date", "required": True},
        {"name": "end_date", "label": "End Date", "type": "date", "required": True},
        {"name": "total_days", "label": "Days", "type": "number", "required": False, "min": 0, "readonly": True},
        {"name": "reason", "label": "Reason", "type": "textarea", "required": False},
        {"name": "approved_by", "label": "Approved By", "type": "select", "required": False, "url_name": "user_select"},
    ],
}

EXTENSION_SECTION = {
    "title": "Extensions",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "membership", "label": "Membership", "type": "select", "required": True, "url_name": "member_membership_select"},
        {"name": "extra_days", "label": "Extra Days", "type": "number", "required": True, "min": 1},
        {"name": "reason", "label": "Reason", "type": "textarea", "required": False},
        {"name": "approved_by", "label": "Approved By", "type": "select", "required": False, "url_name": "user_select"},
    ],
}

UPGRADE_SECTION = {
    "title": "Upgrades",
    "layout": "table",
    "allow_add": True,
    "fields": [
        {"name": "old_membership", "label": "Old Membership", "type": "select", "required": True, "url_name": "member_membership_select"},
        {"name": "new_membership", "label": "New Membership", "type": "select", "required": True, "url_name": "member_membership_select"},
        {"name": "upgrade_date", "label": "Upgrade Date", "type": "date", "required": True},
        {"name": "reason", "label": "Reason", "type": "textarea", "required": False},
    ],
}


def _int_or_none(value):
    value = str(value or "").strip()
    return int(value) if value.isdigit() else None


def _int_or_zero(value):
    parsed = _int_or_none(value)
    return parsed if parsed is not None else 0


def _apply_member_context(item, member, request=None):
    item.member = member
    if hasattr(item, "branch_id") and member.branch_id:
        item.branch = member.branch
    if hasattr(item, "organization_id") and member.organization_id:
        item.organization = member.organization
    if hasattr(item, "fiscal_year_id") and member.fiscal_year_id:
        item.fiscal_year = member.fiscal_year
    if request and hasattr(item, "updated_by_id"):
        item.updated_by = request.user
    if request and not getattr(item, "pk", None) and hasattr(item, "created_by_id"):
        item.created_by = request.user


def _save_rows(request, member, section_name, model, field_names, required_fields, setters):
    rows = parse_dynamic_section(request, section_name)
    existing = {item.id: item for item in model.objects.filter(member=member)}
    keep_ids = []
    for row in rows:
        if not any(row.get(field) for field in field_names):
            continue
        if any(not row.get(field) for field in required_fields):
            continue
        item_id = row.get("id")
        item = existing.get(int(item_id)) if str(item_id or "").isdigit() else model()
        _apply_member_context(item, member, request)
        for field_name, setter in setters.items():
            setattr(item, field_name, setter(row.get(field_name), row, member))
        item.full_clean()
        item.save()
        keep_ids.append(item.id)
    queryset = model.objects.filter(member=member)
    if keep_ids:
        queryset.exclude(id__in=keep_ids).delete()
    else:
        queryset.delete()


def _save_member_membership_sections(request, member):
    active_tab = (request.POST.get("_active_tab") or "").strip()
    if active_tab in {"", "memberships"}:
        _save_rows(
            request,
            member,
            "memberships",
            MemberMembership,
            ["membership_plan", "start_date", "end_date", "total_sessions", "used_sessions", "status", "source", "notes"],
            ["membership_plan", "start_date", "end_date", "status", "source"],
            {
                "membership_plan_id": lambda value, *_args: _int_or_none(value),
                "start_date": lambda value, *_args: value,
                "end_date": lambda value, *_args: value,
                "total_sessions": lambda value, *_args: _int_or_none(value),
                "used_sessions": lambda value, *_args: _int_or_zero(value),
                "status": lambda value, *_args: value or MemberMembership.Status.ACTIVE,
                "source": lambda value, *_args: value or MemberMembership.Source.MANUAL,
                "notes": lambda value, *_args: (value or "").strip(),
            },
        )
    if active_tab in {"", "freezes"}:
        _save_rows(
            request,
            member,
            "freezes",
            MembershipFreeze,
            ["membership", "start_date", "end_date", "reason", "approved_by"],
            ["membership", "start_date", "end_date"],
            {
                "membership_id": lambda value, *_args: _int_or_none(value),
                "start_date": lambda value, *_args: value,
                "end_date": lambda value, *_args: value,
                "reason": lambda value, *_args: (value or "").strip(),
                "approved_by_id": lambda value, *_args: _int_or_none(value),
            },
        )
    if active_tab in {"", "extensions"}:
        rows = parse_dynamic_section(request, "extensions")
        existing = {
            item.id: item
            for item in MembershipExtension.objects.filter(membership__member=member)
        }
        keep_ids = []
        for row in rows:
            if not any(row.get(field) for field in ["membership", "extra_days", "reason", "approved_by"]):
                continue
            if not row.get("membership") or not row.get("extra_days"):
                continue
            item_id = row.get("id")
            item = existing.get(int(item_id)) if str(item_id or "").isdigit() else MembershipExtension()
            item.membership_id = _int_or_none(row.get("membership"))
            item.extra_days = _int_or_zero(row.get("extra_days"))
            item.reason = (row.get("reason") or "").strip()
            item.approved_by_id = _int_or_none(row.get("approved_by"))
            if member.branch_id:
                item.branch = member.branch
            if member.organization_id:
                item.organization = member.organization
            if member.fiscal_year_id:
                item.fiscal_year = member.fiscal_year
            if hasattr(item, "updated_by_id"):
                item.updated_by = request.user
            if not getattr(item, "pk", None) and hasattr(item, "created_by_id"):
                item.created_by = request.user
            item.full_clean()
            item.save()
            keep_ids.append(item.id)
        queryset = MembershipExtension.objects.filter(membership__member=member)
        if keep_ids:
            queryset.exclude(id__in=keep_ids).delete()
        else:
            queryset.delete()
    if active_tab in {"", "upgrades"}:
        _save_rows(
            request,
            member,
            "upgrades",
            MembershipUpgrade,
            ["old_membership", "new_membership", "upgrade_date", "reason"],
            ["old_membership", "new_membership", "upgrade_date"],
            {
                "old_membership_id": lambda value, *_args: _int_or_none(value),
                "new_membership_id": lambda value, *_args: _int_or_none(value),
                "upgrade_date": lambda value, *_args: value,
                "reason": lambda value, *_args: (value or "").strip(),
            },
        )


def _load_member_membership_sections(member, request=None):
    return {
        "memberships": [
            {
                "id": item.id,
                "membership_plan": str(item.membership_plan_id),
                "start_date": encode_date_for_display(item.start_date, request),
                "end_date": encode_date_for_display(item.end_date, request),
                "total_sessions": item.total_sessions or "",
                "used_sessions": item.used_sessions,
                "remaining_sessions": item.remaining_sessions if item.remaining_sessions is not None else "",
                "status": item.status,
                "source": item.source,
                "notes": item.notes,
            }
            for item in member.memberships.order_by("-start_date", "-id")
        ],
        "freezes": [
            {
                "id": item.id,
                "membership": str(item.membership_id),
                "start_date": encode_date_for_display(item.start_date, request),
                "end_date": encode_date_for_display(item.end_date, request),
                "total_days": item.total_days,
                "reason": item.reason,
                "approved_by": str(item.approved_by_id or ""),
            }
            for item in member.membership_freezes.order_by("-start_date", "-id")
        ],
        "extensions": [
            {
                "id": item.id,
                "membership": str(item.membership_id),
                "extra_days": item.extra_days,
                "reason": item.reason,
                "approved_by": str(item.approved_by_id or ""),
            }
            for item in MembershipExtension.objects.filter(membership__member=member).order_by("-created_at", "-id")
        ],
        "upgrades": [
            {
                "id": item.id,
                "old_membership": str(item.old_membership_id),
                "new_membership": str(item.new_membership_id),
                "upgrade_date": encode_date_for_display(item.upgrade_date, request),
                "reason": item.reason,
            }
            for item in member.membership_upgrades.order_by("-upgrade_date", "-id")
        ],
    }


register_entity(
    EntityConfig(
        name="member",
        url_path="members",
        verbose_name="Member",
        model=Member,
        form_class=MemberForm,
        datatable_view=MemberDataTableView,
        fields=[],
        tabs=[
            {
                "key": "party",
                "label": "Party",
                "fields": [
                    {
                        "name": "party_name",
                        "label": "Party Name",
                        "required": True,
                        "col": 6,
                        "type": "text",
                        "placeholder": "Member full name",
                    },
                    {
                        "name": "party_display_name",
                        "label": "Display Name",
                        "type": "text",
                        "required": False,
                        "col": 6,
                        "placeholder": "Optional display name",
                    },
                    {
                        "name": "party_type",
                        "label": "Party Type",
                        "type": "select",
                        "required": True,
                        "col": 4,
                        "url_name": "party_type_select",
                    },
                   
                    {
                        "name": "party_is_active",
                        "label": "Party Active",
                        "type": "checkbox",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "party_remarks",
                        "label": "Party Notes",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                        "placeholder": "Notes saved to Party master",
                    },
                ],
            },
            {
                "key": "membership",
                "label": "Membership",
                "requires_id": True,
                "fields": [
                    {
                        "name": "member_code",
                        "label": "Member Code",
                        "type": "text",
                        "required": False,
                        "col": 6,
                        "placeholder": "Auto-generated if left blank",
                    },
                    {
                        "name": "join_date",
                        "label": "Join Date",
                        "type": "date",
                        "required": True,
                        "col": 4,
                        "calendar_switchable": False,
                        "calendar_mode": "ad",
                    },
                    {
                        "name": "status",
                        "label": "Status",
                        "type": "select",
                        "required": True,
                        "col": 4,
                        "url_name": "member_status_select",
                    },
                    {
                        "name": "branch",
                        "label": "Branch",
                        "type": "select",
                        "required": True,
                        "col": 4,
                        "url_name": "branch_select",
                    },
                    {
                        "name": "emergency_contact_name",
                        "label": "Emergency Contact Name",
                        "type": "text",
                        "required": False,
                        "col": 6,
                    },
                    {
                        "name": "emergency_contact_phone",
                        "label": "Emergency Contact Phone",
                        "type": "text",
                        "required": False,
                        "col": 6,
                    },
                    {
                        "name": "remarks",
                        "label": "Notes",
                        "type": "textarea",
                        "required": False,
                        "col": 12,
                        "placeholder": "Notes saved to Member record",
                    },
                ],
            },
            {
                "key": "profile",
                "label": "Profile",
                "requires_id": True,
                "fields": [
                    {
                        "name": "date_of_birth",
                        "label": "Date of Birth",
                        "type": "date",
                        "required": False,
                        "col": 4,
                        "calendar_switchable": False,
                        "calendar_mode": "ad",
                    },
                    {
                        "name": "gender",
                        "label": "Gender",
                        "type": "static_select",
                        "required": False,
                        "col": 4,
                        "options": [("", "Select Gender"), *PartyIndividualProfile.GENDER_CHOICES],
                    },
                    {
                        "name": "fitness_goals",
                        "label": "Fitness Goals",
                        "type": "checkbox_table",
                        "required": False,
                        "col": 12,
                        "options": lambda _request=None: [
                            {
                                "value": goal.pk,
                                "label": goal.name,
                                "code": goal.code,
                                "remarks": goal.remarks,
                            }
                            for goal in FitnessGoal.objects.order_by("name")
                        ],
                    },
                    {
                        "name": "activity_level",
                        "label": "Activity Level",
                        "type": "select",
                        "required": False,
                        "col": 4,
                        "url_name": "activity_level_select",
                    },
                    {
                        "name": "height",
                        "label": "Height",
                        "type": "number",
                        "required": False,
                        "col": 3,
                        "step": "0.01",
                        "min": 0,
                    },
                    {
                        "name": "weight",
                        "label": "Weight",
                        "type": "number",
                        "required": False,
                        "col": 3,
                        "step": "0.01",
                        "min": 0,
                    },
                    {
                        "name": "bmi",
                        "label": "BMI",
                        "type": "number",
                        "required": False,
                        "col": 3,
                        "step": "0.01",
                        "min": 0,
                    },
                    {
                        "name": "body_fat_percentage",
                        "label": "Body Fat %",
                        "type": "number",
                        "required": False,
                        "col": 3,
                        "step": "0.01",
                        "min": 0,
                    },
                    {
                        "name": "photo",
                        "label": "Photo",
                        "type": "file",
                        "required": False,
                        "col": 4,
                    },
                    {
                        "name": "medical_conditions",
                        "label": "Medical Conditions",
                        "type": "textarea",
                        "required": False,
                        "col": 6,
                    },
                    {
                        "name": "injuries",
                        "label": "Injuries",
                        "type": "textarea",
                        "required": False,
                        "col": 6,
                    },
                ],
            },
            {
                "key": "memberships",
                "label": "Memberships",
                "requires_id": True,
                "fields": [],
                "sections": ["memberships"],
            },
            {
                "key": "freezes",
                "label": "Freezes",
                "requires_id": True,
                "fields": [],
                "sections": ["freezes"],
            },
            {
                "key": "extensions",
                "label": "Extensions",
                "requires_id": True,
                "fields": [],
                "sections": ["extensions"],
            },
            {
                "key": "upgrades",
                "label": "Upgrades",
                "requires_id": True,
                "fields": [],
                "sections": ["upgrades"],
            },
        ],
        dynamic_sections={
            "memberships": MEMBERSHIP_SECTION,
            "freezes": FREEZE_SECTION,
            "extensions": EXTENSION_SECTION,
            "upgrades": UPGRADE_SECTION,
        },
        dynamic_sections_loader=_load_member_membership_sections,
        dynamic_sections_saver=_save_member_membership_sections,
        datatable_columns=[
            {
                "name": key,
                "title": key.replace("_", " ").title() if key != "party" else "Party",
            }
            for key, _accessor in MEMBER_COLUMNS
            if key != "id"
        ],
        reset_defaults={"party_is_active": True},
        select_search_fields=["member_code", "party__name", "party__display_name", "branch__name"],
        select_label_func=lambda obj: f"{obj.member_code} - {obj.party.display_name or obj.party.name}",
    )
)

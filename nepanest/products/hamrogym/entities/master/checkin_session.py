from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from core.config import EntityConfig
from core.registry import register_entity

from ...datatables.checkin_session_data_table import CHECKIN_SESSION_COLUMNS, CheckinSessionDataTableView
from ...forms.checkin_session_form import CheckinSessionForm
from ...models import CheckinSession, Member, MemberCheckin, MemberMembership


def _get_active_membership(member):
    today = timezone.localdate()
    return (
        MemberMembership.objects.filter(
            member=member,
            status=MemberMembership.Status.ACTIVE,
            start_date__lte=today,
            end_date__gte=today,
        )
        .select_related("membership_plan")
        .order_by("-start_date", "-id")
        .first()
    )


def _check_in_member(request, member):
    today = timezone.localdate()
    open_checkin = member.checkins.filter(checkout_time__isnull=True).first()
    if open_checkin:
        raise ValidationError({"__all__": ["Member is already checked in."]})

    if member.checkins.filter(checkin_time__date=today).exists():
        raise ValidationError({"__all__": ["Member has already completed today's session."]})

    membership = _get_active_membership(member)
    if not membership:
        raise ValidationError({"__all__": ["Member does not have an active membership for today."]})

    now = timezone.now()
    with transaction.atomic():
        checkin = MemberCheckin(
            member=member,
            member_membership=membership,
            checkin_time=now,
            checkin_type=MemberCheckin.CheckinType.GYM,
            source=MemberCheckin.Source.MANUAL,
        )
        if hasattr(checkin, "created_by_id"):
            checkin.created_by = request.user
        if hasattr(checkin, "updated_by_id"):
            checkin.updated_by = request.user
        checkin.full_clean()
        checkin.save()

        session = CheckinSession(
            member_checkin=checkin,
            start_time=now,
        )
        if hasattr(session, "created_by_id"):
            session.created_by = request.user
        if hasattr(session, "updated_by_id"):
            session.updated_by = request.user
        session.full_clean()
        session.save()

    member_name = member.party.display_name or member.party.name
    return {"message": f"{member_name} checked in successfully."}


def _check_out_member(request, member):
    open_checkin = (
        member.checkins.filter(checkout_time__isnull=True)
        .prefetch_related("sessions")
        .first()
    )
    if not open_checkin:
        raise ValidationError({"__all__": ["Member is not currently checked in."]})

    now = timezone.now()
    with transaction.atomic():
        for session in open_checkin.sessions.filter(end_time__isnull=True):
            session.end_time = now
            if hasattr(session, "updated_by_id"):
                session.updated_by = request.user
            session.full_clean()
            session.save()

        if hasattr(open_checkin, "updated_by_id"):
            open_checkin.updated_by = request.user
        open_checkin.mark_checkout(checkout_time=now, save=True)

    member_name = member.party.display_name or member.party.name
    return {"message": f"{member_name} checked out successfully."}


register_entity(
    EntityConfig(
        name="checkin_session",
        url_path="checkin-sessions",
        verbose_name="Checkin Session",
        model=Member,
        form_class=CheckinSessionForm,
        datatable_view=CheckinSessionDataTableView,
        template_name="hamrogym/checkin_sessions/index.html",
        fields=[],
        datatable_columns=[
            {
                "name": key,
                "title": {
                    "member_code": "Member Code",
                    "member_name": "Member Name",
                    "membership_plan": "Membership Plan",
                    "checkin_time": "Check In Time",
                    "checkout_time": "Check Out Time",
                    "session_state": "Status",
                }.get(key, key.replace("_", " ").title()),
                **(
                    {
                        "render": (
                            "function(data){"
                            "const styles={"
                            "'Ready for Check In':'success',"
                            "'Checked In':'warning',"
                            "'Checked Out':'secondary',"
                            "'No Active Membership':'dark'"
                            "};"
                            "const tone=styles[data]||'light';"
                            "return `<span class=\"badge text-bg-${tone}\">${data || ''}</span>`;"
                            "}"
                        )
                    }
                    if key == "session_state"
                    else {}
                ),
            }
            for key, _accessor in CHECKIN_SESSION_COLUMNS
            if key != "id"
        ],
        row_actions={
            "check_in": _check_in_member,
            "check_out": _check_out_member,
        },
        action_buttons=[
            {
                "action_name": "check_in",
                "title": "Check In Member",
                "label": "Check In",
                "icon_class": "fas fa-right-to-bracket",
                "class_name": "btn-outline-success",
                "confirm_text": "Record check in for this member?",
                "hide_on_values": ["checked_in", "checked_out", "membership_inactive"],
            },
            {
                "action_name": "check_out",
                "title": "Check Out Member",
                "label": "Check Out",
                "icon_class": "fas fa-right-from-bracket",
                "class_name": "btn-outline-warning",
                "confirm_text": "Record check out for this member?",
                "hide_on_values": ["not_checked_in", "checked_out", "membership_inactive"],
            },
        ],
        action_state_field="session_state",
        show_create=False,
        show_view=False,
        select_search_fields=["member_code", "party__name", "party__display_name"],
        select_label_func=lambda obj: f"{obj.member_code} - {obj.party.display_name or obj.party.name}",
    )
)

from django.db.models import Case, CharField, DateTimeField, F, OuterRef, Subquery, Value, When
from django.utils.timezone import localdate

from nepanest.common.helpers.helper import encode_datetime_for_display

from core.datatables.views import BaseDataTableView

from ..models import Member, MemberCheckin, MemberMembership


CHECKIN_SESSION_COLUMNS = [
    ("id", "id"),
    ("member_code", "member_code"),
    ("member_name", lambda obj: obj.party.display_name or obj.party.name),
    ("membership_plan", lambda obj: obj.active_membership_plan_name or ""),
    ("checkin_time", lambda obj, request: encode_datetime_for_display(obj.last_checkin_time, request)),
    ("checkout_time", lambda obj, request: encode_datetime_for_display(obj.last_checkout_time, request)),
    (
        "session_state",
        lambda obj: {
            "not_checked_in": "Ready for Check In",
            "checked_in": "Checked In",
            "checked_out": "Checked Out",
            "membership_inactive": "No Active Membership",
        }.get(obj.session_state, "Unknown"),
    ),
    ("branch", lambda obj: obj.branch.name if obj.branch_id else ""),
]


class CheckinSessionDataTableView(BaseDataTableView):
    model = Member
    columns = CHECKIN_SESSION_COLUMNS
    searchable_columns = [
        "member_code",
        "party__name",
        "party__display_name",
        "branch__name",
        "active_membership_plan_name",
        "session_state",
    ]
    orderable_columns = [
        "member_code",
        "party__name",
        "active_membership_plan_name",
        "last_checkin_time",
        "last_checkout_time",
        "session_state",
        "branch__name",
    ]

    def get_queryset(self):
        today = localdate()
        open_checkins = MemberCheckin.objects.filter(
            member=OuterRef("pk"),
            checkout_time__isnull=True,
        ).order_by("-checkin_time", "-id")
        today_checkins = MemberCheckin.objects.filter(
            member=OuterRef("pk"),
            checkin_time__date=today,
        ).order_by("-checkin_time", "-id")
        active_memberships = MemberMembership.objects.filter(
            member=OuterRef("pk"),
            status=MemberMembership.Status.ACTIVE,
            start_date__lte=today,
            end_date__gte=today,
        ).order_by("-start_date", "-id")

        return (
            self.model.objects.select_related("party", "branch")
            .annotate(
                open_checkin_id=Subquery(open_checkins.values("id")[:1]),
                open_checkin_time=Subquery(open_checkins.values("checkin_time")[:1]),
                today_last_checkin_time=Subquery(today_checkins.values("checkin_time")[:1]),
                today_last_checkout_time=Subquery(today_checkins.values("checkout_time")[:1]),
                active_membership_id=Subquery(active_memberships.values("id")[:1]),
                active_membership_plan_name=Subquery(active_memberships.values("membership_plan__name")[:1]),
            )
            .annotate(
                session_state=Case(
                    When(open_checkin_id__isnull=False, then=Value("checked_in")),
                    When(today_last_checkin_time__isnull=False, then=Value("checked_out")),
                    When(active_membership_id__isnull=True, then=Value("membership_inactive")),
                    default=Value("not_checked_in"),
                    output_field=CharField(),
                ),
                last_checkin_time=Case(
                    When(open_checkin_time__isnull=False, then=F("open_checkin_time")),
                    default=F("today_last_checkin_time"),
                    output_field=DateTimeField(),
                ),
                last_checkout_time=Case(
                    When(open_checkin_id__isnull=False, then=Value(None)),
                    default=F("today_last_checkout_time"),
                    output_field=DateTimeField(),
                ),
            )
            .order_by("member_code", "id")
        )

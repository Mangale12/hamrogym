from datetime import date, timedelta
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max, Q
from django.http import JsonResponse
from django.urls import NoReverseMatch, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from core.models import Party
from nepanest.products.hamrogym.forms import (
    WorkoutAssignmentForm,
    WorkoutDayForm,
    WorkoutExerciseForm,
    WorkoutLogForm,
    WorkoutPlanForm,
    WorkoutWeekForm,
)
from nepanest.products.hamrogym.models import (
    ClassAttendance,
    ClassBooking,
    ClassCancellation,
    ClassSession,
    ClassSchedule,
    ClassWaitlist,
    Member,
    PersonalBest,
    Trainer,
    WorkoutAssignment,
    WorkoutDay,
    WorkoutExercise,
    WorkoutLog,
    WorkoutPlan,
    WorkoutPlanVersion,
    WorkoutWeek,
)

SCHEDULE_WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _resolve_url(url_name):
    try:
        return reverse(url_name)
    except NoReverseMatch:
        return "#"


@login_required
def dashboard(request):
    from django.contrib.auth import get_user_model
    from nepanest.modules.people.models import Department, Employee
    from nepanest.modules.recruitment.models import Applicant, JobPosting, JobRequisition

    User = get_user_model()

    users = User.objects.all()
    employees = Employee.objects.all()
    requisitions = JobRequisition.objects.all()
    applicants = Applicant.objects.select_related("job_posting").all()
    job_postings = JobPosting.objects.select_related("job_position").all()

    context = {
        "stats": [
            {
                "label": "System Users",
                "value": users.count(),
                "subtitle": f"{users.filter(is_staff=True).count()} with staff access",
                "icon": "users",
                "theme": "sky",
            },
            {
                "label": "Active Employees",
                "value": employees.filter(is_active=True).count(),
                "subtitle": f"{Department.objects.filter(is_active=True).count()} active departments",
                "icon": "briefcase",
                "theme": "emerald",
            },
            {
                "label": "Open Job Posts",
                "value": job_postings.filter(is_active=True).count(),
                "subtitle": f"{requisitions.filter(status='pending').count()} pending requisitions",
                "icon": "clipboard",
                "theme": "amber",
            },
            {
                "label": "Applicants",
                "value": applicants.count(),
                "subtitle": f"{applicants.filter(status='pending').count()} pending review",
                "icon": "user-plus",
                "theme": "rose",
            },
        ],
        "quick_links": [
            {
                "title": "Manage Users",
                "description": "Create login accounts and assign system access.",
                "url_name": "user_list",
                "url": _resolve_url("user_list"),
                "icon": "shield",
            },
            {
                "title": "Employees",
                "description": "Maintain employee records and work assignments.",
                "url_name": "employee_list",
                "url": _resolve_url("employee_list"),
                "icon": "users",
            },
            {
                "title": "Departments",
                "description": "Keep organization units and structures updated.",
                "url_name": "department_list",
                "url": _resolve_url("department_list"),
                "icon": "layers",
            },
            {
                "title": "Recruitment",
                "description": "Track openings, requisitions, and applicants.",
                "url_name": "job_posting_list",
                "url": _resolve_url("job_posting_list"),
                "icon": "target",
            },
        ],
        "module_groups": [
            {
                "title": "Front Desk and Staff",
                "summary": "Shared people and HR modules supporting reception, staffing, and shift coordination.",
                "links": [
                    {"label": "Users", "url": _resolve_url("user_list")},
                    {"label": "Employees", "url": _resolve_url("employee_list")},
                    {"label": "Departments", "url": _resolve_url("department_list")},
                    {"label": "Holiday Calendar", "url": _resolve_url("holiday_calendar_view")},
                ],
            },
            {
                "title": "Hiring Pipeline",
                "summary": "Trainer, operations, and support hiring can still run on the reusable recruitment stack.",
                "links": [
                    {"label": "Job Postings", "url": _resolve_url("job_posting_list")},
                    {"label": "Job Requisitions", "url": _resolve_url("job_requisition_list")},
                    {"label": "Applicants", "url": _resolve_url("applicant_list")},
                ],
            },
            {
                "title": "Back Office",
                "summary": "Accounting, assets, and tasks remain shared so HamroGym can focus on product-specific workflows.",
                "links": [
                    {"label": "Task Board", "url": _resolve_url("task_board")},
                    {"label": "Assets", "url": _resolve_url("asset_list")},
                    {"label": "Journal Entries", "url": _resolve_url("journal_entry_list")},
                ],
            },
        ],
        "focus_areas": [
            {
                "title": "Membership Operations",
                "description": "Use this product surface to grow member onboarding, plans, renewals, and reception flows.",
                "icon": "user-check",
            },
            {
                "title": "Coach Scheduling",
                "description": "Keep trainer availability, class assignments, and performance tools product-owned here.",
                "icon": "clock",
            },
            {
                "title": "Gym Analytics",
                "description": "Add attendance, retention, and revenue dashboards without touching the shared engine.",
                "icon": "bar-chart-2",
            },
        ],
        "operations_panels": [
            {
                "label": "Front Desk",
                "value": users.filter(is_active=True).count(),
                "description": "Active user accounts available for reception, admin, and operator workflows.",
                "icon": "monitor",
            },
            {
                "label": "Team Floor",
                "value": employees.filter(is_active=True).count(),
                "description": "Current active employee records available for coaching and team coordination.",
                "icon": "users",
            },
            {
                "label": "Hiring Queue",
                "value": applicants.filter(status='pending').count(),
                "description": "Candidates still waiting for review before joining the HamroGym team.",
                "icon": "user-plus",
            },
        ],
        "dashboard_lanes": [
            {
                "title": "Member Journey",
                "description": "Keep leads, signups, renewals, attendance, and retention in a gym-first workflow rather than a generic ERP homepage.",
                "icon": "heart",
            },
            {
                "title": "Coaching Desk",
                "description": "Plan trainer availability, classes, and follow-up from a product surface designed for gym operations.",
                "icon": "calendar",
            },
            {
                "title": "Operations Console",
                "description": "Give reception and management teams a simpler command center while the shared platform still handles reusable records.",
                "icon": "grid",
            },
        ],
        "separation_points": [
            {
                "title": "Dedicated HamroGym Layout",
                "description": "This dashboard now resolves through a HamroGym-only template namespace instead of relying on the shared layout name.",
                "icon": "layout",
            },
            {
                "title": "Product-Owned Messaging",
                "description": "The hero area, actions, and sections now describe HamroGym operations instead of the generic Nepanest product view.",
                "icon": "type",
            },
            {
                "title": "Shared Modules, Separate Home",
                "description": "People, hiring, tasks, assets, and finance can stay shared without forcing HamroGym to share the same dashboard design.",
                "icon": "link",
            },
        ],
        "recent_users": users.order_by("-date_joined")[:5],
        "recent_applicants": applicants.order_by("-created_at")[:5],
        "recent_requisitions": requisitions.select_related("department", "designation").order_by("-created_at")[:5],
    }
    return render(request, "hamrogym/dashboard.html", context)


@login_required
def member_available_party_select(request):
    term = (request.GET.get("term") or request.GET.get("q") or "").strip()
    page = max(int(request.GET.get("page", 1) or 1), 1)
    page_size = min(max(int(request.GET.get("page_size", 20) or 20), 1), 100)
    ids_param = (request.GET.get("ids") or request.GET.get("id") or "").strip()

    queryset = Party.objects.filter(category="individual").order_by("name", "id")

    if ids_param:
        ids = [int(value) for value in ids_param.split(",") if value.strip().isdigit()]
        queryset = queryset.filter(pk__in=ids)
        results = [
            {"id": obj.pk, "text": obj.display_name or obj.name}
            for obj in queryset
        ]
        return JsonResponse({"results": results, "pagination": {"more": False}})

    queryset = queryset.filter(hamrogym_member__isnull=True)
    if term:
        queryset = queryset.filter(
            Q(name__icontains=term)
            | Q(display_name__icontains=term)
            | Q(pan_number__icontains=term)
            | Q(vat_number__icontains=term)
        )

    start = (page - 1) * page_size
    items = list(queryset[start : start + page_size + 1])
    more = len(items) > page_size
    items = items[:page_size]

    return JsonResponse(
        {
            "results": [{"id": obj.pk, "text": obj.display_name or obj.name} for obj in items],
            "pagination": {"more": more},
        }
    )


def _build_class_schedule_queryset():
    return ClassSchedule.objects.select_related(
        "gym_class__class_type",
        "class_room",
        "trainer__employee__user",
        "branch",
    ).prefetch_related(
        "sessions__trainer__employee__user",
        "sessions__bookings__member__party",
        "sessions__attendance_records__member__party",
        "sessions__waitlists__member__party",
        "sessions__cancellation",
    )


def _class_schedule_alert(request):
    status = (request.GET.get("status") or "").strip()
    created = int(request.GET.get("created", 0) or 0)
    skipped = int(request.GET.get("skipped", 0) or 0)
    session_date = request.GET.get("session_date", "")

    if status == "sessions-generated":
        if created and skipped:
            return ("success", f"Generated {created} session(s). Skipped {skipped} existing session(s).")
        if created:
            return ("success", f"Generated {created} session(s) successfully.")
        return ("warning", f"No new sessions were generated. Skipped {skipped} existing session(s).")
    if status == "session-added":
        return ("success", f"Manual session created for {session_date}.")
    if status == "session-cancelled":
        return ("success", f"Session on {session_date} was cancelled.")
    if status == "session-completed":
        return ("success", f"Session on {session_date} was marked completed.")
    if status == "trainer-updated":
        return ("success", f"Trainer assignment updated for {session_date}.")
    if status == "booking-added":
        return ("success", f"Booking added for session on {session_date}.")
    if status == "attendance-saved":
        return ("success", f"Attendance saved for session on {session_date}.")
    if status == "waitlist-added":
        return ("success", f"Member added to waitlist for session on {session_date}.")
    if status == "waitlist-promoted":
        return ("success", f"Waitlisted member promoted into session on {session_date}.")
    if status == "invalid-range":
        return ("danger", "End date must be on or after start date.")
    if status == "invalid-weekday":
        return ("danger", "This schedule has an invalid day of week and cannot generate sessions.")
    return None


def _build_class_schedule_context(request, schedule, *, generator_initial=None):
    today = timezone.localdate()
    upcoming_sessions = list(
        schedule.sessions.select_related("trainer__employee__user").filter(
            session_date__gte=today
        ).order_by("session_date", "start_time")
    )
    past_sessions = list(
        schedule.sessions.select_related("trainer__employee__user").filter(
            session_date__lt=today
        ).order_by("-session_date", "-start_time")
    )
    all_sessions = upcoming_sessions + past_sessions
    completed_count = sum(1 for session in all_sessions if session.status == "completed")
    cancelled_count = sum(1 for session in all_sessions if session.status == "cancelled")
    scheduled_count = sum(1 for session in all_sessions if session.status == "scheduled")

    initial = generator_initial or {
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=56)).isoformat(),
    }
    manual_initial = {
        "session_date": today.isoformat(),
        "start_time": schedule.start_time.strftime("%H:%M") if schedule.start_time else "",
        "end_time": schedule.end_time.strftime("%H:%M") if schedule.end_time else "",
        "trainer_id": str(schedule.trainer_id or ""),
        "max_capacity": schedule.gym_class.max_capacity if schedule.gym_class_id else "",
    }

    return {
        "schedule": schedule,
        "upcoming_sessions": upcoming_sessions,
        "past_sessions": past_sessions,
        "session_summary": {
            "total": len(all_sessions),
            "upcoming": len(upcoming_sessions),
            "completed": completed_count,
            "cancelled": cancelled_count,
            "scheduled": scheduled_count,
            "next_session": upcoming_sessions[0] if upcoming_sessions else None,
        },
        "today": today,
        "alert": _class_schedule_alert(request),
        "generator_initial": initial,
        "manual_initial": manual_initial,
        "active_trainers": Trainer.objects.filter(status=Trainer.Status.ACTIVE).select_related("employee__user").order_by("employee__employee_id"),
        "active_members": Member.objects.select_related("party").filter(is_active=True).order_by("member_code"),
        "attendance_status_choices": ClassAttendance._meta.get_field("status").choices,
        "cancellation_actor_choices": ClassCancellation._meta.get_field("cancelled_by").choices,
    }


def _redirect_schedule_detail(schedule, status, **params):
    query = urlencode({key: value for key, value in {"status": status, **params}.items() if value not in (None, "")})
    return redirect(f"{reverse('hamrogym_class_schedule_view', args=[schedule.pk])}?{query}")


class ClassScheduleDetailView(LoginRequiredMixin, View):
    template_name = "hamrogym/class_schedules/detail.html"

    def get(self, request, pk):
        schedule = get_object_or_404(_build_class_schedule_queryset(), pk=pk)
        return render(request, self.template_name, _build_class_schedule_context(request, schedule))

    def post(self, request, pk):
        schedule = get_object_or_404(_build_class_schedule_queryset(), pk=pk)
        action = (request.POST.get("action") or "generate").strip()

        if action == "generate":
            return self._generate_sessions(request, schedule)
        if action == "manual_add":
            return self._manual_add_session(request, schedule)
        if action == "cancel_session":
            return self._cancel_session(request, schedule)
        if action == "change_trainer":
            return self._change_session_trainer(request, schedule)
        if action == "complete_session":
            return self._complete_session(request, schedule)
        if action == "add_booking":
            return self._add_booking(request, schedule)
        if action == "mark_attendance":
            return self._mark_attendance(request, schedule)
        if action == "add_waitlist":
            return self._add_waitlist(request, schedule)
        if action == "promote_waitlist":
            return self._promote_waitlist(request, schedule)

        context = _build_class_schedule_context(request, schedule)
        context["alert"] = ("danger", "Unsupported schedule session action.")
        return render(request, self.template_name, context, status=400)

    def _generate_sessions(self, request, schedule):
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        generator_initial = {
            "start_date": start_date or "",
            "end_date": end_date or "",
        }

        if not start_date or not end_date:
            context = _build_class_schedule_context(request, schedule, generator_initial=generator_initial)
            context["alert"] = ("danger", "Start date and end date are required to generate sessions.")
            return render(request, self.template_name, context, status=400)

        try:
            start_date = date.fromisoformat(start_date)
            end_date = date.fromisoformat(end_date)
        except ValueError:
            context = _build_class_schedule_context(request, schedule, generator_initial=generator_initial)
            context["alert"] = ("danger", "Enter valid dates to generate schedule sessions.")
            return render(request, self.template_name, context, status=400)

        if end_date < start_date:
            return _redirect_schedule_detail(schedule, "invalid-range")

        target_weekday = SCHEDULE_WEEKDAY_MAP.get(schedule.day_of_week)
        if target_weekday is None:
            return _redirect_schedule_detail(schedule, "invalid-weekday")

        created_count = 0
        skipped_count = 0
        cursor = start_date

        while cursor <= end_date:
            if cursor.weekday() == target_weekday:
                session, created = ClassSession.objects.get_or_create(
                    class_schedule=schedule,
                    session_date=cursor,
                    defaults={
                        "start_time": schedule.start_time,
                        "end_time": schedule.end_time,
                        "trainer": schedule.trainer,
                        "max_capacity": schedule.gym_class.max_capacity,
                        "status": "scheduled",
                        "branch": schedule.branch,
                        "organization": schedule.organization,
                        "fiscal_year": schedule.fiscal_year,
                    },
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1
            cursor += timedelta(days=1)

        return _redirect_schedule_detail(schedule, "sessions-generated", created=created_count, skipped=skipped_count)

    def _manual_add_session(self, request, schedule):
        session_date_raw = request.POST.get("session_date", "").strip()
        start_time_raw = request.POST.get("start_time", "").strip()
        end_time_raw = request.POST.get("end_time", "").strip()
        trainer_id = request.POST.get("trainer", "").strip()
        max_capacity_raw = request.POST.get("max_capacity", "").strip()

        context = _build_class_schedule_context(request, schedule)
        context["manual_initial"] = {
            "session_date": session_date_raw,
            "start_time": start_time_raw,
            "end_time": end_time_raw,
            "trainer_id": trainer_id,
            "max_capacity": max_capacity_raw,
        }

        try:
            session_date = date.fromisoformat(session_date_raw)
        except ValueError:
            context["alert"] = ("danger", "Enter a valid session date for the manual session.")
            return render(request, self.template_name, context, status=400)

        try:
            start_time = datetime.strptime(start_time_raw, "%H:%M").time()
            end_time = datetime.strptime(end_time_raw, "%H:%M").time()
        except ValueError:
            context["alert"] = ("danger", "Enter valid start and end times for the manual session.")
            return render(request, self.template_name, context, status=400)

        try:
            max_capacity = int(max_capacity_raw)
        except (TypeError, ValueError):
            context["alert"] = ("danger", "Enter a valid max capacity for the manual session.")
            return render(request, self.template_name, context, status=400)

        trainer = None
        if trainer_id:
            trainer = Trainer.objects.filter(pk=trainer_id, status=Trainer.Status.ACTIVE).first()
            if trainer is None:
                context["alert"] = ("danger", "Select a valid active trainer for the manual session.")
                return render(request, self.template_name, context, status=400)

        try:
            with transaction.atomic():
                session = ClassSession(
                    class_schedule=schedule,
                    session_date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                    trainer=trainer or schedule.trainer,
                    max_capacity=max_capacity,
                    status="scheduled",
                    branch=schedule.branch,
                    organization=schedule.organization,
                    fiscal_year=schedule.fiscal_year,
                )
                if hasattr(session, "created_by_id"):
                    session.created_by = request.user
                if hasattr(session, "updated_by_id"):
                    session.updated_by = request.user
                session.full_clean()
                session.save()
        except ValidationError as exc:
            message = " ".join(sum((messages if isinstance(messages, list) else [str(messages)] for messages in getattr(exc, "message_dict", {}).values()), [])) or "Manual session could not be created."
            context["alert"] = ("danger", message)
            return render(request, self.template_name, context, status=400)

        return _redirect_schedule_detail(schedule, "session-added", session_date=session.session_date.isoformat())

    def _get_schedule_session(self, request, schedule):
        session_id = request.POST.get("session_id", "").strip()
        return get_object_or_404(ClassSession.objects.select_related("class_schedule", "trainer__employee__user"), pk=session_id, class_schedule=schedule)

    def _cancel_session(self, request, schedule):
        session = self._get_schedule_session(request, schedule)
        cancelled_by = request.POST.get("cancelled_by", "").strip() or "admin"
        reason = request.POST.get("reason", "").strip()
        cancellation, _created = ClassCancellation.objects.get_or_create(
            class_session=session,
            defaults={
                "cancelled_by": cancelled_by,
                "reason": reason,
                "branch": schedule.branch,
                "organization": schedule.organization,
                "fiscal_year": schedule.fiscal_year,
            },
        )
        if not _created:
            cancellation.cancelled_by = cancelled_by
            cancellation.reason = reason
        if hasattr(cancellation, "created_by_id") and _created:
            cancellation.created_by = request.user
        if hasattr(cancellation, "updated_by_id"):
            cancellation.updated_by = request.user
        cancellation.full_clean()
        cancellation.save()
        return _redirect_schedule_detail(schedule, "session-cancelled", session_date=session.session_date.isoformat())

    def _complete_session(self, request, schedule):
        session = self._get_schedule_session(request, schedule)
        session.status = "completed"
        if hasattr(session, "updated_by_id"):
            session.updated_by = request.user
        session.save(update_fields=["status", "updated_by", "updated_at"] if hasattr(session, "updated_by_id") else ["status", "updated_at"])
        return _redirect_schedule_detail(schedule, "session-completed", session_date=session.session_date.isoformat())

    def _change_session_trainer(self, request, schedule):
        session = self._get_schedule_session(request, schedule)
        trainer_id = request.POST.get("trainer", "").strip()
        trainer = None
        if trainer_id:
            trainer = get_object_or_404(Trainer.objects.filter(status=Trainer.Status.ACTIVE), pk=trainer_id)
        session.trainer = trainer
        if hasattr(session, "updated_by_id"):
            session.updated_by = request.user
        try:
            session.full_clean()
            session.save()
        except ValidationError as exc:
            context = _build_class_schedule_context(request, schedule)
            message = " ".join(sum((messages if isinstance(messages, list) else [str(messages)] for messages in getattr(exc, "message_dict", {}).values()), [])) or "Trainer update failed."
            context["alert"] = ("danger", message)
            return render(request, self.template_name, context, status=400)
        return _redirect_schedule_detail(schedule, "trainer-updated", session_date=session.session_date.isoformat())

    def _add_booking(self, request, schedule):
        session = self._get_schedule_session(request, schedule)
        member_id = request.POST.get("member", "").strip()
        context = _build_class_schedule_context(request, schedule)

        if not member_id:
            context["alert"] = ("danger", "Select a member to create a booking.")
            return render(request, self.template_name, context, status=400)

        member = get_object_or_404(Member.objects.filter(is_active=True), pk=member_id)
        try:
            booking = ClassBooking(
                class_session=session,
                member=member,
                status="booked",
                branch=schedule.branch,
                organization=schedule.organization,
                fiscal_year=schedule.fiscal_year,
            )
            if hasattr(booking, "created_by_id"):
                booking.created_by = request.user
            if hasattr(booking, "updated_by_id"):
                booking.updated_by = request.user
            booking.full_clean()
            booking.save()
        except ValidationError as exc:
            message = " ".join(sum((messages if isinstance(messages, list) else [str(messages)] for messages in getattr(exc, "message_dict", {}).values()), [])) or "Booking could not be created."
            context["alert"] = ("danger", message)
            return render(request, self.template_name, context, status=400)
        return _redirect_schedule_detail(schedule, "booking-added", session_date=session.session_date.isoformat())

    def _mark_attendance(self, request, schedule):
        session = self._get_schedule_session(request, schedule)
        member_id = request.POST.get("member", "").strip()
        attendance_status = request.POST.get("attendance_status", "").strip() or "present"
        context = _build_class_schedule_context(request, schedule)

        if not member_id:
            context["alert"] = ("danger", "Select a member to mark attendance.")
            return render(request, self.template_name, context, status=400)

        member = get_object_or_404(Member.objects.filter(is_active=True), pk=member_id)
        booking = ClassBooking.objects.filter(class_session=session, member=member).first()
        checked_in_at = timezone.now() if attendance_status in {"present", "late"} else None

        try:
            attendance, created = ClassAttendance.objects.get_or_create(
                class_session=session,
                member=member,
                defaults={
                    "booking": booking,
                    "status": attendance_status,
                    "checked_in_at": checked_in_at,
                    "branch": schedule.branch,
                    "organization": schedule.organization,
                    "fiscal_year": schedule.fiscal_year,
                    "created_by": request.user if hasattr(ClassAttendance, "created_by") else None,
                    "updated_by": request.user if hasattr(ClassAttendance, "updated_by") else None,
                },
            )
            if not created:
                attendance.booking = booking
                attendance.status = attendance_status
                attendance.checked_in_at = checked_in_at
                if hasattr(attendance, "updated_by_id"):
                    attendance.updated_by = request.user
                attendance.full_clean()
                attendance.save()
        except ValidationError as exc:
            message = " ".join(sum((messages if isinstance(messages, list) else [str(messages)] for messages in getattr(exc, "message_dict", {}).values()), [])) or "Attendance could not be saved."
            context["alert"] = ("danger", message)
            return render(request, self.template_name, context, status=400)

        return _redirect_schedule_detail(schedule, "attendance-saved", session_date=session.session_date.isoformat())

    def _add_waitlist(self, request, schedule):
        session = self._get_schedule_session(request, schedule)
        member_id = request.POST.get("member", "").strip()
        context = _build_class_schedule_context(request, schedule)

        if not member_id:
            context["alert"] = ("danger", "Select a member to add to the waitlist.")
            return render(request, self.template_name, context, status=400)

        member = get_object_or_404(Member.objects.filter(is_active=True), pk=member_id)
        next_position = (session.waitlists.aggregate(Max("waitlist_position")).get("waitlist_position__max") or 0) + 1
        try:
            waitlist = ClassWaitlist(
                class_session=session,
                member=member,
                waitlist_position=next_position,
                branch=schedule.branch,
                organization=schedule.organization,
                fiscal_year=schedule.fiscal_year,
            )
            if hasattr(waitlist, "created_by_id"):
                waitlist.created_by = request.user
            if hasattr(waitlist, "updated_by_id"):
                waitlist.updated_by = request.user
            waitlist.full_clean()
            waitlist.save()
        except ValidationError as exc:
            message = " ".join(sum((messages if isinstance(messages, list) else [str(messages)] for messages in getattr(exc, "message_dict", {}).values()), [])) or "Waitlist entry could not be created."
            context["alert"] = ("danger", message)
            return render(request, self.template_name, context, status=400)
        return _redirect_schedule_detail(schedule, "waitlist-added", session_date=session.session_date.isoformat())

    def _promote_waitlist(self, request, schedule):
        session = self._get_schedule_session(request, schedule)
        waitlist_id = request.POST.get("waitlist_id", "").strip()
        waitlist = get_object_or_404(ClassWaitlist.objects.select_related("member"), pk=waitlist_id, class_session=session)
        context = _build_class_schedule_context(request, schedule)

        active_bookings = session.bookings.filter(status="booked").count()
        if active_bookings >= session.max_capacity:
            context["alert"] = ("danger", "Session is still at full capacity. Cancel a booking first or increase capacity before promoting.")
            return render(request, self.template_name, context, status=400)

        try:
            with transaction.atomic():
                booking = ClassBooking(
                    class_session=session,
                    member=waitlist.member,
                    status="booked",
                    branch=schedule.branch,
                    organization=schedule.organization,
                    fiscal_year=schedule.fiscal_year,
                )
                if hasattr(booking, "created_by_id"):
                    booking.created_by = request.user
                if hasattr(booking, "updated_by_id"):
                    booking.updated_by = request.user
                booking.full_clean()
                booking.save()

                waitlist.promoted_at = timezone.now()
                if hasattr(waitlist, "updated_by_id"):
                    waitlist.updated_by = request.user
                waitlist.save(update_fields=["promoted_at", "updated_by", "updated_at"] if hasattr(waitlist, "updated_by_id") else ["promoted_at", "updated_at"])
                waitlist.delete()

                remaining = session.waitlists.order_by("waitlist_position", "id")
                for index, item in enumerate(remaining, start=1):
                    if item.waitlist_position != index:
                        item.waitlist_position = index
                        item.save(update_fields=["waitlist_position", "updated_at"])
        except ValidationError as exc:
            message = " ".join(sum((messages if isinstance(messages, list) else [str(messages)] for messages in getattr(exc, "message_dict", {}).values()), [])) or "Waitlist promotion failed."
            context["alert"] = ("danger", message)
            return render(request, self.template_name, context, status=400)

        return _redirect_schedule_detail(schedule, "waitlist-promoted", session_date=session.session_date.isoformat())


def _workout_plan_alert(request):
    status = (request.GET.get("status") or "").strip()
    alerts = {
        "plan-created": ("success", "Workout plan created successfully."),
        "plan-updated": ("success", "Workout plan updated successfully."),
        "week-added": ("success", "Week added to the workout structure."),
        "week-deleted": ("success", "Week removed from the workout structure."),
        "day-added": ("success", "Day added to the workout structure."),
        "day-deleted": ("success", "Day removed from the workout structure."),
        "exercise-added": ("success", "Exercise added to the workout day."),
        "exercise-deleted": ("success", "Exercise removed from the workout day."),
        "assignment-created": ("success", "Workout assignment created successfully."),
        "log-created": ("success", "Workout log created successfully."),
        "log-created-pb": ("success", "Workout log saved and a personal best was updated."),
    }
    return alerts.get(status)


def _build_workout_plan_queryset():
    return WorkoutPlan.objects.select_related("fitness_goal").prefetch_related(
        "workout_weeks",
        "workout_weeks__days",
        "workout_weeks__days__exercises",
        "workout_weeks__days__exercises__exercise",
        "versions",
    )


def _create_workout_plan_version(plan, change_notes):
    latest_version = plan.versions.order_by("-version_number").first()
    next_version = 1 if latest_version is None else latest_version.version_number + 1
    return WorkoutPlanVersion.objects.create(
        workout_plan=plan,
        version_number=next_version,
        change_notes=change_notes,
    )


def _update_personal_best_from_log(log):
    if not log.exercise_id:
        return None

    metrics_present = any(
        value is not None
        for value in (log.weight_used, log.reps_completed, log.duration_seconds)
    )
    if not metrics_present:
        return None

    personal_best, _created = PersonalBest.objects.get_or_create(
        member=log.member,
        exercise=log.exercise,
        defaults={
            "best_weight": log.weight_used,
            "best_reps": log.reps_completed,
            "best_duration": log.duration_seconds,
            "achieved_on": log.date,
        },
    )

    changed = False
    if log.weight_used is not None and (personal_best.best_weight is None or log.weight_used > personal_best.best_weight):
        personal_best.best_weight = log.weight_used
        changed = True
    if log.reps_completed is not None and (personal_best.best_reps is None or log.reps_completed > personal_best.best_reps):
        personal_best.best_reps = log.reps_completed
        changed = True
    if log.duration_seconds is not None and (personal_best.best_duration is None or log.duration_seconds > personal_best.best_duration):
        personal_best.best_duration = log.duration_seconds
        changed = True

    if changed:
        personal_best.achieved_on = log.date
        personal_best.save()
        return personal_best

    return None


def _workout_plan_context(
    request,
    *,
    plan=None,
    form=None,
    active_tab="overview",
    week_form=None,
    day_form=None,
    day_error_week_id=None,
    exercise_form=None,
    exercise_error_day_id=None,
):
    plans = None
    if plan is None:
        plans = WorkoutPlan.objects.select_related("fitness_goal").order_by("name")

    structure = []
    total_days = 0
    total_exercises = 0
    active_week_id = None
    recent_versions = []
    if plan is not None:
        weeks = (
            plan.workout_weeks.all()
            .order_by("week_number", "id")
            .prefetch_related("days__exercises__exercise")
        )
        structure = list(weeks)
        for week in structure:
            days = list(week.days.all().order_by("day_number", "id"))
            week.prefetched_days = days
            week.exercise_count = 0
            total_days += len(days)
            for day in days:
                exercises = list(day.exercises.all().order_by("sequence_order", "id"))
                day.prefetched_exercises = exercises
                week.exercise_count += len(exercises)
                total_exercises += len(exercises)
        recent_versions = list(plan.versions.all()[:6])
        if day_error_week_id:
            active_week_id = day_error_week_id
        elif exercise_error_day_id:
            for week in structure:
                if any(day.pk == exercise_error_day_id for day in week.prefetched_days):
                    active_week_id = week.pk
                    break
        elif structure:
            active_week_id = structure[0].pk

    alert = _workout_plan_alert(request)
    return {
        "plans": plans,
        "plan": plan,
        "form": form or WorkoutPlanForm(instance=plan),
        "week_form": week_form or WorkoutWeekForm(workout_plan=plan),
        "blank_day_form": WorkoutDayForm(workout_plan=plan),
        "day_form": day_form or WorkoutDayForm(workout_plan=plan),
        "day_error_week_id": day_error_week_id,
        "blank_exercise_form": WorkoutExerciseForm(),
        "exercise_form": exercise_form or WorkoutExerciseForm(),
        "exercise_error_day_id": exercise_error_day_id,
        "structure": structure,
        "active_week_id": active_week_id,
        "total_days": total_days,
        "total_exercises": total_exercises,
        "recent_versions": recent_versions,
        "active_tab": active_tab,
        "alert": alert,
    }


class WorkoutPlanCreateView(LoginRequiredMixin, View):
    def get(self, request):
        context = _workout_plan_context(request, form=WorkoutPlanForm())
        return render(request, "hamrogym/workout_plans/form.html", context)

    def post(self, request):
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            _create_workout_plan_version(plan, "Initial workout plan created.")
            return redirect(f"{reverse('hamrogym_workout_plan_structure', args=[plan.pk])}?status=plan-created")
        context = _workout_plan_context(request, form=form)
        return render(request, "hamrogym/workout_plans/form.html", context, status=400)


class WorkoutPlanUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        plan = get_object_or_404(WorkoutPlan.objects.select_related("fitness_goal"), pk=pk)
        context = _workout_plan_context(request, plan=plan, form=WorkoutPlanForm(instance=plan))
        return render(request, "hamrogym/workout_plans/form.html", context)

    def post(self, request, pk):
        plan = get_object_or_404(WorkoutPlan, pk=pk)
        form = WorkoutPlanForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save()
            _create_workout_plan_version(plan, "Workout plan metadata updated.")
            return redirect(f"{reverse('hamrogym_workout_plan_structure', args=[plan.pk])}?status=plan-updated")
        context = _workout_plan_context(request, plan=plan, form=form)
        return render(request, "hamrogym/workout_plans/form.html", context, status=400)


class WorkoutPlanDetailView(LoginRequiredMixin, View):
    template_name = "hamrogym/workout_plans/detail.html"

    def get(self, request, pk, tab="overview"):
        plan = get_object_or_404(_build_workout_plan_queryset(), pk=pk)
        active_tab = "structure" if tab == "structure" else "overview"
        context = _workout_plan_context(request, plan=plan, active_tab=active_tab)
        return render(request, self.template_name, context)


class WorkoutWeekCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        plan = get_object_or_404(_build_workout_plan_queryset(), pk=pk)
        form = WorkoutWeekForm(request.POST, workout_plan=plan)
        if form.is_valid():
            week = form.save(commit=False)
            week.workout_plan = plan
            week.save()
            _create_workout_plan_version(plan, f"Added Week {week.week_number}.")
            return redirect(f"{reverse('hamrogym_workout_plan_structure', args=[plan.pk])}?status=week-added")
        context = _workout_plan_context(request, plan=plan, active_tab="structure", week_form=form)
        return render(request, "hamrogym/workout_plans/detail.html", context, status=400)


class WorkoutWeekDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, week_id):
        plan = get_object_or_404(WorkoutPlan, pk=pk)
        week = get_object_or_404(WorkoutWeek, pk=week_id, workout_plan=plan)
        week_number = week.week_number
        week.days.all().delete()
        week.delete()
        _create_workout_plan_version(plan, f"Removed Week {week_number}.")
        return redirect(f"{reverse('hamrogym_workout_plan_structure', args=[plan.pk])}?status=week-deleted")


class WorkoutDayCreateView(LoginRequiredMixin, View):
    def post(self, request, pk, week_id):
        plan = get_object_or_404(WorkoutPlan, pk=pk)
        week = get_object_or_404(WorkoutWeek, pk=week_id, workout_plan=plan)
        form = WorkoutDayForm(request.POST, workout_week=week, workout_plan=plan)
        if form.is_valid():
            day = form.save(commit=False)
            day.workout_plan = plan
            day.workout_week = week
            day.save()
            _create_workout_plan_version(plan, f"Added Day {day.day_number}: {day.title}.")
            return redirect(f"{reverse('hamrogym_workout_plan_structure', args=[plan.pk])}?status=day-added")
        plan = get_object_or_404(_build_workout_plan_queryset(), pk=pk)
        context = _workout_plan_context(
            request,
            plan=plan,
            active_tab="structure",
            day_form=form,
            day_error_week_id=week.pk,
        )
        return render(request, "hamrogym/workout_plans/detail.html", context, status=400)


class WorkoutDayDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, day_id):
        plan = get_object_or_404(WorkoutPlan, pk=pk)
        day = get_object_or_404(WorkoutDay, pk=day_id, workout_plan=plan)
        day_label = f"Day {day.day_number}: {day.title}"
        day.delete()
        _create_workout_plan_version(plan, f"Removed {day_label}.")
        return redirect(f"{reverse('hamrogym_workout_plan_structure', args=[plan.pk])}?status=day-deleted")


class WorkoutExerciseCreateView(LoginRequiredMixin, View):
    def post(self, request, pk, day_id):
        plan = get_object_or_404(WorkoutPlan, pk=pk)
        day = get_object_or_404(WorkoutDay, pk=day_id, workout_plan=plan)
        form = WorkoutExerciseForm(request.POST)
        if form.is_valid():
            workout_exercise = form.save(commit=False)
            workout_exercise.workout_day = day
            try:
                workout_exercise.full_clean()
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                workout_exercise.save()
                _create_workout_plan_version(
                    plan,
                    f"Added exercise {workout_exercise.exercise.name} to Day {day.day_number}.",
                )
                return redirect(f"{reverse('hamrogym_workout_plan_structure', args=[plan.pk])}?status=exercise-added")
        plan = get_object_or_404(_build_workout_plan_queryset(), pk=pk)
        context = _workout_plan_context(
            request,
            plan=plan,
            active_tab="structure",
            exercise_form=form,
            exercise_error_day_id=day.pk,
        )
        return render(request, "hamrogym/workout_plans/detail.html", context, status=400)


class WorkoutExerciseDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, exercise_id):
        plan = get_object_or_404(WorkoutPlan, pk=pk)
        workout_exercise = get_object_or_404(
            WorkoutExercise,
            pk=exercise_id,
            workout_day__workout_plan=plan,
        )
        exercise_label = workout_exercise.exercise.name
        day_number = workout_exercise.workout_day.day_number
        workout_exercise.delete()
        _create_workout_plan_version(plan, f"Removed exercise {exercise_label} from Day {day_number}.")
        return redirect(f"{reverse('hamrogym_workout_plan_structure', args=[plan.pk])}?status=exercise-deleted")


class WorkoutAssignmentCreateView(LoginRequiredMixin, View):
    def get(self, request):
        initial = {}
        workout_plan_id = request.GET.get("workout_plan")
        if workout_plan_id:
            initial["workout_plan"] = workout_plan_id
        return render(
            request,
            "hamrogym/workout_assignments/form.html",
            {
                "form": WorkoutAssignmentForm(initial=initial),
                "alert": _workout_plan_alert(request),
            },
        )

    def post(self, request):
        form = WorkoutAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            return redirect(f"{reverse('hamrogym_workout_assignment_create')}?status=assignment-created&id={assignment.pk}")
        return render(request, "hamrogym/workout_assignments/form.html", {"form": form}, status=400)


class WorkoutLogCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            "hamrogym/workout_logs/form.html",
            {
                "form": WorkoutLogForm(),
                "alert": _workout_plan_alert(request),
                "recent_personal_bests": PersonalBest.objects.select_related("member", "exercise").order_by("-achieved_on", "-id")[:6],
            },
        )

    def post(self, request):
        form = WorkoutLogForm(request.POST)
        if form.is_valid():
            log = form.save()
            personal_best = _update_personal_best_from_log(log)
            status = "log-created-pb" if personal_best else "log-created"
            return redirect(f"{reverse('hamrogym_workout_log_create')}?status={status}&id={log.pk}")
        return render(
            request,
            "hamrogym/workout_logs/form.html",
            {
                "form": form,
                "recent_personal_bests": PersonalBest.objects.select_related("member", "exercise").order_by("-achieved_on", "-id")[:6],
            },
            status=400,
        )

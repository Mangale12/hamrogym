from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.urls import NoReverseMatch, reverse
from django.shortcuts import get_object_or_404, redirect, render
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
    PersonalBest,
    WorkoutAssignment,
    WorkoutDay,
    WorkoutExercise,
    WorkoutLog,
    WorkoutPlan,
    WorkoutPlanVersion,
    WorkoutWeek,
)


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

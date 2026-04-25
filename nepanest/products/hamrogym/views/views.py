from django.contrib.auth.decorators import login_required
from django.urls import NoReverseMatch, reverse
from django.shortcuts import render


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

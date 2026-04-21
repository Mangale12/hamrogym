from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request):
    from django.contrib.auth import get_user_model
    from Nepanest.hr.models import Applicant, Department, Employee, JobPosting, JobRequisition

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
                "icon": "shield",
            },
            {
                "title": "Employees",
                "description": "Maintain employee records and work assignments.",
                "url_name": "employee_list",
                "icon": "users",
            },
            {
                "title": "Departments",
                "description": "Keep organization units and structures updated.",
                "url_name": "department_list",
                "icon": "layers",
            },
            {
                "title": "Recruitment",
                "description": "Track openings, requisitions, and applicants.",
                "url_name": "job_posting_list",
                "icon": "target",
            },
        ],
        "recent_users": users.order_by("-date_joined")[:5],
        "recent_applicants": applicants.order_by("-created_at")[:5],
        "recent_requisitions": requisitions.select_related("department", "designation").order_by("-created_at")[:5],
    }
    return render(request, "index.html", context)

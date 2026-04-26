SIDEBAR_ITEMS = [
    {
        "label": "Dashboard Home",
        "icon": "home",
        "url_name": "dashboard",
        "match": "/product/hamrogym/dashboard/",
    },
    {
        "label": "Gym Operations",
        "icon": "activity",
        "children": [
            {
                "label": "Front Desk",
                "url": "#",
                "disabled": True,
            },
            {
                "label": "Memberships",
                "url": "#",
                "disabled": True,
                "badge": "Soon",
            },
            {
                "label": "Trainer Schedule",
                "url": "#",
                "disabled": True,
            },
        ],
    },
    {
        "label": "People and Staff",
        "icon": "users",
        "children": [
            {
                "label": "Users",
                "url_name": "user_list",
            },
            {
                "label": "Employees",
                "url_name": "employee_list",
            },
            {
                "label": "Members",
                "url_name": "member_list",
            },
            {
                "label": "Departments",
                "url_name": "department_list",
            },
        ],
    },
    {
        "label": "Recruitment",
        "icon": "user-plus",
        "children": [
            {
                "label": "Job Postings",
                "url_name": "job_posting_list",
            },
            {
                "label": "Job Requisitions",
                "url_name": "job_requisition_list",
            },
            {
                "label": "Applicants",
                "url_name": "applicant_list",
            },
        ],
    },
    {
        "label": "Master Setup",
        "icon": "briefcase",
        "children": [
            {
                "label": "Gym Facilities",
                "url_name": "gym_facility_list",
            },
            {
                "label": "Assets",
                "url_name": "asset_list",
            },
            {
                "label": "Journal Entries",
                "url_name": "journal_entry_list",
            },
        ],
    },
]

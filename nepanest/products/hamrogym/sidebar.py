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
                "label": "Member Memberships",
                "url_name": "member_membership_list",
            },
            {
                "label": "Membership Freezes",
                "url_name": "membership_freeze_list",
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
                "label": "Member Referrals",
                "url_name": "member_referral_list",
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
                "label": "Access Types",
                "url_name": "access_type_list",
            },
            {
                "label": "Membership Plans",
                "url_name": "membership_plan_list",
            },
            {
                "label": "Gym Facilities",
                "url_name": "gym_facility_list",
            },
            {
                "label": "Member Statuses",
                "url_name": "member_status_list",
            },
            {
                "label": "Fitness Goals",
                "url_name": "fitness_goal_list",
            },
            
            {
                "label": "Activity Levels",
                "url_name": "activity_level_list",
            },
            {
                "label": "Member Tags",
                "url_name": "member_tag_list",
            },
        ],
    },
]

SIDEBAR_ITEMS = [
    {
        "label": "Workforce",
        "icon": "users",
        "children": [
            {
                "label": "Employees",
                "icon": "user-check",
                "url_name": "employee_list",
                "match": "/core/employees",
            },
            {
                "label": "Departments",
                "icon": "layers",
                "url_name": "department_list",
                "match": "/core/departments",
            },
            {
                "label": "Designations",
                "icon": "briefcase",
                "url_name": "designation_list",
                "match": "/core/designations",
            },
            {
                "label": "Team Roles",
                "icon": "shield",
                "url_name": "team_role_list",
                "match": "/core/team-roles",
            },
            {
                "label": "Teams",
                "icon": "git-branch",
                "url_name": "team_list",
                "match": "/core/teams",
            },
            {
                "label": "Employment Types",
                "icon": "users",
                "url_name": "employeement_type_list",
                "match": "/core/employeement-types",
            },
            {
                "label": "Shifts",
                "icon": "clock",
                "url_name": "shift_list",
                "match": "/core/shifts",
            },
            {
                "label": "Shift Rotations",
                "icon": "repeat",
                "url_name": "employee_shift_list",
                "match": "/core/employee-shifts",
            },
        ],
    }
]

__all__ = ["SIDEBAR_ITEMS"]

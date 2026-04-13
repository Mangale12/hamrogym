SIDEBAR_ITEMS = [
    {
        "label": "Task Management",
        "icon": "settings",
        "children": [
            {
                "label": "Master Setup",
                "icon": "tag",
                "children": [
                    {
                        "label": "Task Types",
                        "icon": "tag",
                        "url_name": "task_type_list",
                        "match": "/core/task-types",
                    },
                    {
                        "label": "Task Status",
                        "icon": "tag",
                        "url_name": "task_status_list",
                        "match": "/core/task-statuses",
                    },
                    {
                        "label": "Task Labels",
                        "icon": "tag",
                        "url_name": "task_label_list",
                        "match": "/core/task-labels",
                    },
                    {
                        "label": "Task Modules",
                        "icon": "tag",
                        "url_name": "task_module_list",
                        "match": "/core/task-modules",
                    },
                    {
                        "label": "Checklist",
                        "icon": "tag",
                        "url_name": "checklist_list",
                        "match": "/core/checklists",
                    }
                ],
            },
            {
                "label": "Projects",
                "icon": "project",
                "url_name": "project_list",
                "match": "/core/projects",
            },
            {
                "label": "Tasks",
                "icon": "check-square",
                "url_name": "task_list",
                "match": "/core/tasks",
            },
            {
                "label": "Task Board",
                "icon": "columns",
                "url_name": "task_board",
                "match": "/core/tasks/board",
            },
        ],
    },
]

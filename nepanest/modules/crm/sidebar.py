SIDEBAR_ITEMS = [
    {
        "label": "CRM",
        "icon": "briefcase",
        "children": [
            {
                "label": "Dashboard",
                "icon": "home",
                "url": "/core/crm/dashboard/",
                "match": "/core/crm/dashboard",
            },
            {
                "label": "Leads",
                "icon": "user-plus",
                "url_name": "crm_lead_list",
                "match": "/core/crm/leads",
            },
            {
                "label": "Lead Board",
                "icon": "columns",
                "url_name": "crm_lead_list",
                "match": "/core/crm/leads",
            },
            {
                "label": "Contacts",
                "icon": "users",
                "url_name": "crm_contact_list",
                "match": "/crm/contacts",
            },
            {
                "label": "Companies",
                "icon": "building",
                "url_name": "crm_company_list",
                "match": "/crm/companies",
            },
            {
                "label": "Deals",
                "icon": "target",
                "url_name": "crm_deal_list",
                "match": "/crm/deals",
            },
            {
                "label": "Activities",
                "icon": "calendar",
                "url_name": "crm_activity_list",
                "match": "/crm/activities",
            },
            {
                "label": "Lead Sources",
                "icon": "calendar",
                "url_name": "lead_source_list",
                "match": "/core/lead-sources",
            },
            {
                "label": "Lead Statuses",
                "icon": "tag",
                "url_name": "lead_status_list",
                "match": "/core/lead-statuses",
            },
            {
                "label" : "Service Types",
                "icon": "tag",
                "url_name": "service_type_list",
                "match": "/core/service-types",
            },
             {
                "label" : "Services",
                "icon": "tag",
                "url_name": "service_list",
                "match": "/core/services",
            }
        ],
    }
]

__all__ = ["SIDEBAR_ITEMS"]

SIDEBAR_ITEMS = [
    {
        "label": "CRM",
        "icon": "briefcase",
        "children": [
            {
                "label": "Dashboard",
                "icon": "home",
                "url_name": "crm_dashboard",
                "match": "/crm/dashboard",
            },
            {
                "label": "Leads",
                "icon": "user-plus",
                "url_name": "crm_lead_list",
                "match": "/crm/leads",
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
                "match": "/crm/lead-sources",
            },
        ],
    }
]

__all__ = ["SIDEBAR_ITEMS"]

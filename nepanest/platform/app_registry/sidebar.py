SIDEBAR_ITEMS = [
    {
        "label": "Dashboard",
        "icon": "layout-dashboard",
        "url_name": "dashboard",
        "namespace": "registry",
        "match": "/platform/app-registry/",
    },
    {
        "label": "Registry",
        "icon": "database",
        "children": [
            {
                "label": "Clients",
                "url_name": "client_list",
                "namespace": "registry",
                "match": "/platform/app-registry/clients",
            },
            {
                "label": "Tenant DBs",
                "url_name": "tenant_db_list",
                "namespace": "registry",
                "match": "/platform/app-registry/tenant-dbs",
            },
            {
                "label": "Licenses",
                "url_name": "license_list",
                "namespace": "registry",
                "match": "/platform/app-registry/licenses",
            },
            {
                "label": "License Renew History",
                "url_name": "license_renew_history_list",
                "namespace": "registry",
                "match": "/platform/app-registry/license-renew-history",
            },
            {
                "label": "Subscriptions",
                "url_name": "subscription_list",
                "namespace": "registry",
                "match": "/platform/app-registry/subscriptions",
            },
        ],
    },
]

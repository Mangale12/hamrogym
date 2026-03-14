from django.urls import NoReverseMatch, reverse


def sidebar_items(request):
    items = [
        {
            "label": "Dashboard",
            "icon": "home",
            "url_name": "dashboard",
            "match": "/",
        },
        {
            "label": "Users",
            "icon": "users",
            "url": "#",
        },
        {
            "label": "Members",
            "icon": "user",
            "url": "#",
        },
        {
            "label": "Trainers",
            "icon": "briefcase",
            "url": "#",
        },
        {
            "label": "Attendance",
            "icon": "calendar",
            "url": "#",
        },
        {
            "label": "Payments",
            "icon": "credit-card",
            "url": "#",
        },
        {
            "label": "Reports",
            "icon": "bar-chart-2",
            "url": "#",
        },
        {
            "label": "Settings",
            "icon": "settings",
            "url": "#",
        },
    ]

    path = request.path or "/"

    for item in items:
        url = item.get("url")
        url_name = item.get("url_name")
        if (not url or url == "#") and url_name:
            try:
                url = reverse(url_name)
            except NoReverseMatch:
                url = "#"
        item["url"] = url

        match = item.get("match") or url
        if match in (None, "", "#"):
            item["is_active"] = False
        elif match == "/":
            item["is_active"] = path == "/"
        else:
            item["is_active"] = path.startswith(match.rstrip("/"))

    return {"sidebar_items": items}

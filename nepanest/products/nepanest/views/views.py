from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render


@login_required
def dashboard(request):
    context = {
        "platform_hero": {
            "eyebrow": "Platform Operations",
            "title": "Platform Dashboard",
            "subtitle": "A dedicated control center for platform-wide workflows, rollout tracking, and shared services.",
        },
        "platform_metrics": [
            {
                "label": "Live Route",
                "value": "/platform/dashboard/",
                "description": "The first platform route now resolves through the platform layout automatically.",
            },
            {
                "label": "Layout Mode",
                "value": "Path-based",
                "description": "Any request whose first URL segment is `platform` uses the platform shell.",
            },
            {
                "label": "Current Scope",
                "value": "1 page",
                "description": "This first rollout keeps the change focused while we add the rest of the platform surface.",
            },
            {
                "label": "Next Step",
                "value": "Sidebar",
                "description": "The next slice can add a platform-specific navigation tree and module shortcuts.",
            },
        ],
        "platform_actions": [
            {
                "label": "Open platform home",
                "url": reverse("platform_dashboard"),
                "description": "Return to the dedicated platform entry point.",
                "variant": "primary",
            },
            {
                "label": "Go to HamroGym",
                "url": reverse("dashboard"),
                "description": "Switch back to the product dashboard that still powers the gym workflow.",
                "variant": "outline-secondary",
            },
            {
                "label": "Review shared modules",
                "url": "/core/",
                "description": "Check the shared ERP modules that the platform can reuse.",
                "variant": "outline-dark",
            },
        ],
        "platform_sections": [
            {
                "title": "Rollout status",
                "bullets": [
                    "Platform URLs now start with `/platform/`.",
                    "The layout resolver selects a dedicated platform shell.",
                    "The first landing page now looks like a real admin home.",
                ],
            },
            {
                "title": "What comes next",
                "bullets": [
                    "Add platform-only sidebar items.",
                    "Move more management pages into the platform namespace.",
                    "Create reusable cards for platform-wide settings and health checks.",
                ],
            },
        ]
    }
    return render(request, "platform/dashboard.html", context)

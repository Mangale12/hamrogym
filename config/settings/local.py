from .base import *  # noqa: F403
from importlib.util import find_spec


def _show_toolbar(request):
    if request.path.startswith("/__debug__/"):
        return False
    if request.method != "GET":
        return False
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return False
    accept = request.headers.get("accept", "")
    if "application/json" in accept or "application/javascript" in accept or "text/javascript" in accept:
        return False
    return True


DEBUG = True
ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Browsers ignore COOP on plain http custom domains like hamrogym.local and
# emit noisy warnings during local development.
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

if find_spec("debug_toolbar"):
    INSTALLED_APPS = [*INSTALLED_APPS, "debug_toolbar"]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
]

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
    "SHOW_TOOLBAR_CALLBACK": _show_toolbar,
}

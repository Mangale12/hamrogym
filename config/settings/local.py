from .base import *  # noqa: F403


DEBUG = True
ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Browsers ignore COOP on plain http custom domains like hamrogym.local and
# emit noisy warnings during local development.
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

INSTALLED_APPS = [*INSTALLED_APPS, "debug_toolbar"]
MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    *MIDDLEWARE,
]

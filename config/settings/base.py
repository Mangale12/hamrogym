import os
from importlib.util import find_spec
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key:
            os.environ.setdefault(key, value)


load_env_file(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-@r82)ls0m(4n%kh)@j)-_z@bjrej#^jd%!5$1*enw@^*@ll1zx",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

HOST_URLCONF_MAP = {
    "127.0.0.1": "config.urls",
    "crm.local": "config.urlconfs.crm",
    "crm.nepanest.local": "config.urlconfs.crm",
    "localhost": "config.urls",
    "hamrogym.local": "config.urls",
    "hamrogym.nepanest.local": "config.urls",
    "nepanest.local": "config.urlconfs.nepanest",
}

PRODUCT_SUBDOMAIN_BASE_DOMAIN = os.environ.get(
    "DJANGO_PRODUCT_SUBDOMAIN_BASE_DOMAIN",
    "nepanest.local",
).strip().lower()

PRODUCT_SUBDOMAIN_URLCONFS = {
    "crm": "config.urlconfs.crm",
    "hamrogym": "config.urls",
    "nepanest": "config.urlconfs.nepanest",
}


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "nepanest.products.hamrogym.apps.HamroGymConfig",
    "nepanest.products.nepanest.apps.NepanestProductConfig",
    "nepanest.modules.crm.apps.CRMModuleConfig",
    "nepanest.modules.people.apps.PeopleModuleConfig",
    "nepanest.modules.human_resources.apps.HumanResourcesModuleConfig",
    "nepanest.modules.assets.apps.AssetsModuleConfig",
    "nepanest.modules.finance.apps.FinanceModuleConfig",
    "core.apps.CoreConfig",
    "nepanest.modules.tasks.apps.TaskModuleConfig",
    "nepanest.modules.billing.apps.BillingModuleConfig",
    "nepanest.modules.accounting.apps.AccountingConfig",
]

if find_spec("django_extensions"):
    INSTALLED_APPS.append("django_extensions")

MIDDLEWARE = [
    "nepanest.common.middlewares.dump_and_die.DumpAndDieMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "nepanest.common.middlewares.host_routing.HostURLConfMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "nepanest.common.middlewares.bs_date_converter.BSDateConverterMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "nepanest.common.helpers.context.organization_context",
                "nepanest.products.hamrogym.context_processors.base_layout_template",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.mysql"),
        "NAME": os.environ.get("DB_NAME", "db_erp_hamrogym"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "M@ngal12"),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "3306"),
    }
}

MIGRATION_MODULES = {
    "account": "nepanest.modules.accounting.migrations",
    "assets": "nepanest.modules.assets.migrations",
    "billing": "nepanest.modules.billing.migrations",
    "finance": "nepanest.modules.finance.migrations",
    "hr": "nepanest.modules.human_resources.migrations",
    "task": "nepanest.modules.tasks.migrations",
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = []

project_static_dir = BASE_DIR / "static"
if project_static_dir.exists():
    STATICFILES_DIRS.append(project_static_dir)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

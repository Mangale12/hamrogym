from __future__ import annotations

from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView
from django.urls import reverse, reverse_lazy
from core.utils.urls import reverse_with_request
from django.utils import timezone
from django.views.generic import TemplateView
from django.db import connection


from core.views.auth import RememberMeLoginView

from .datatables.client_data_table import CLIENT_COLUMNS
from .datatables.license_data_table import LICENSE_COLUMNS
from .datatables.login_history_data_table import LOGIN_HISTORY_COLUMNS
from .datatables.subscription_data_table import SUBSCRIPTION_COLUMNS
from .datatables.tenant_db_data_table import TENANT_DB_COLUMNS
from .models import Client, License, LoginHistory, Subscription, TenantDB


def _datatable_columns(columns):
    return [
        {"name": name, "title": name.replace("_", " ").title()}
        for name, _accessor in columns
        if name != "id"
    ]


class RegistryLoginView(RememberMeLoginView):
    template_name = "platform/app_registry/login.html"
    redirect_authenticated_user = False

    def _namespace(self):
        if self.request.resolver_match:
            return self.request.resolver_match.namespace or "app_registry"
        return "app_registry"

    def get_default_redirect_url(self):
        namespace = self._namespace()
        if namespace == "register":
            return reverse("register:dashboard")
        if namespace == "registry":
            return reverse("registry:dashboard")
        return reverse("app_registry:dashboard")

    def form_valid(self, form):
        
        user = form.get_user()
        if not (user.is_staff or user.is_superuser):
            form.add_error(None, "Registry access is restricted to staff accounts.")
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context.update(
            {
                "next_url": self.request.GET.get(self.redirect_field_name) or self.request.POST.get(self.redirect_field_name),
                "action_url": reverse(f"{self._namespace()}:login"),
                "fields": self._build_fields(form),
                "login_intro": {
                    "kicker": "Registry sign in",
                    "title": "Welcome back",
                    "subtitle": "Use your staff account to access the registry control center.",
                },
            }
        )
        return context

    def _build_fields(self, form):
        return [
            {
                "name": "username",
                "label": form["username"].label,
                "type": "text",
                "required": True,
                "value": form["username"].value() or "",
                "placeholder": form["username"].field.widget.attrs.get("placeholder", "Enter your username"),
                "id": form["username"].id_for_label,
                "errors": list(form["username"].errors),
                "col": 12,
            },
            {
                "name": "password",
                "label": form["password"].label,
                "type": "password",
                "required": True,
                "value": form["password"].value() or "",
                "placeholder": form["password"].field.widget.attrs.get("placeholder", "Enter your password"),
                "id": form["password"].id_for_label,
                "errors": list(form["password"].errors),
                "col": 12,
            },
            {
                "name": "remember_me",
                "label": "Remember me",
                "type": "checkbox",
                "required": False,
                "default": bool(form["remember_me"].value()),
                "id": form["remember_me"].id_for_label,
                "errors": list(form["remember_me"].errors),
                "col": 12,
            },
        ]


class RegistryLogoutView(LogoutView):
    def get_next_page(self):
        namespace = self.request.resolver_match.namespace if self.request.resolver_match else "app_registry"
        if namespace == "register":
            return reverse("register:login")
        if namespace == "registry":
            return reverse("registry:login")
        return reverse("app_registry:login")


class RegistryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("app_registry:login")
    raise_exception = True

    def get_login_url(self):
        namespace = self.request.resolver_match.namespace if self.request.resolver_match else "app_registry"
        if namespace == "register":
            return reverse("register:login")
        if namespace == "registry":
            return reverse("registry:login")
        return reverse("app_registry:login")

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser


class RegistryDashboardView(RegistryAccessMixin, TemplateView):
    template_name = "platform/app_registry/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        context.update(
            {
                "metrics": [
                    {
                        "label": "Clients",
                        "value": Client.objects.count(),
                        "note": "Total registered businesses",
                        "theme": "theme-sky",
                        "icon": "users",
                    },
                    {
                        "label": "Active clients",
                        "value": Client.objects.filter(status=Client.Status.ACTIVE).count(),
                        "note": "Currently in service",
                        "theme": "theme-emerald",
                        "icon": "check-circle",
                    },
                    {
                        "label": "Current licenses",
                        "value": License.objects.filter(is_current=True).count(),
                        "note": "Active billing contracts",
                        "theme": "theme-amber",
                        "icon": "shield",
                    },
                    {
                        "label": "Successful logins",
                        "value": LoginHistory.objects.filter(is_successful=True, logged_in_at__gte=week_ago).count(),
                        "note": "In the last 7 days",
                        "theme": "theme-rose",
                        "icon": "log-in",
                    },
                ],
                "quick_links": [
                    {"label": "Clients", "url": reverse_with_request("client_list", self.request), "icon": "users"},
                    {"label": "Tenant DBs", "url": reverse_with_request("tenant_db_list", self.request), "icon": "database"},
                    {"label": "Licenses", "url": reverse_with_request("license_list", self.request), "icon": "shield"},
                    {"label": "Subscriptions", "url": reverse_with_request("subscription_list", self.request), "icon": "credit-card"},
                    {"label": "Login History", "url": reverse_with_request("login_history_list", self.request), "icon": "activity"},
                ],
                "datatables": [
                    {
                        "key": "clients",
                        "title": "Clients",
                        "description": "Workspace registry, contacts, plan, and status.",
                        "table_id": "registry-clients-table",
                        "ajax_url": reverse_with_request("client_datatable", self.request),
                        "columns": _datatable_columns(CLIENT_COLUMNS),
                        "cta_url": reverse_with_request("client_list", self.request),
                        "datatable_options": {"page_length": 10, "page_length_options": [10, 25, 50]},
                    },
                    {
                        "key": "tenant_dbs",
                        "title": "Tenant DBs",
                        "description": "Database registrations and connection details.",
                        "table_id": "registry-tenant-dbs-table",
                        "ajax_url": reverse_with_request("tenant_db_datatable", self.request),
                        "columns": _datatable_columns(TENANT_DB_COLUMNS),
                        "cta_url": reverse_with_request("tenant_db_list", self.request),
                        "datatable_options": {"page_length": 10, "page_length_options": [10, 25, 50]},
                    },
                    {
                        "key": "licenses",
                        "title": "Licenses",
                        "description": "Current plans, dates, and capacity limits.",
                        "table_id": "registry-licenses-table",
                        "ajax_url": reverse_with_request("license_datatable", self.request),
                        "columns": _datatable_columns(LICENSE_COLUMNS),
                        "cta_url": reverse_with_request("license_list", self.request),
                        "datatable_options": {"page_length": 10, "page_length_options": [10, 25, 50]},
                    },
                    {
                        "key": "subscriptions",
                        "title": "Subscriptions",
                        "description": "Plan billing cycles and subscription health.",
                        "table_id": "registry-subscriptions-table",
                        "ajax_url": reverse_with_request("subscription_datatable", self.request),
                        "columns": _datatable_columns(SUBSCRIPTION_COLUMNS),
                        "cta_url": reverse_with_request("subscription_list", self.request),
                        "datatable_options": {"page_length": 10, "page_length_options": [10, 25, 50]},
                    },
                    {
                        "key": "login_history",
                        "title": "Login History",
                        "description": "Authentication timeline and access outcomes.",
                        "table_id": "registry-login-history-table",
                        "ajax_url": reverse_with_request("login_history_datatable", self.request),
                        "columns": _datatable_columns(LOGIN_HISTORY_COLUMNS),
                        "cta_url": reverse_with_request("login_history_list", self.request),
                        "datatable_options": {"page_length": 10, "page_length_options": [10, 25, 50]},
                    },
                ],
                "page_title": "Registry dashboard",
                "dashboard_intro": {
                    "kicker": "Platform control center",
                    "title": "Manage customers, licenses, and tenant databases from one place.",
                    "subtitle": "Everything in the registry shares the same component system, so tables and forms stay consistent across the platform.",
                },
                "reference_counts": {
                    "total_tenant_dbs": TenantDB.objects.count(),
                    "total_subscriptions": Subscription.objects.count(),
                    "updated_at": now,
                },
            }
        )
        return context

from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.db import DatabaseError

from .context import TenantLookupError, clear_current_tenant, resolve_tenant_by_code, set_current_tenant
from .forms import TenantAwareAuthenticationForm
from .middleware import TenantResolutionMiddleware
from .router import TenantDatabaseRouter


class TenantAwareAuthenticationFormTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_tenant_code_field_is_required_and_labeled(self):
        request = self.factory.get("/accounts/login/")
        form = TenantAwareAuthenticationForm(request=request)

        self.assertIn("tenant_code", form.fields)
        self.assertEqual(form.fields["tenant_code"].label, "Code")
        self.assertEqual(form.fields["tenant_code"].widget.attrs["placeholder"], "Enter workspace code")

    @patch("nepanest.platform.tenancy.forms.resolve_tenant_by_code", side_effect=TenantLookupError("workspace lookup failed"))
    def test_tenant_lookup_database_error_is_exposed_as_form_error(self, _mocked_lookup):
        request = self.factory.post("/accounts/login/", data={"tenant_code": "alpha"})
        form = TenantAwareAuthenticationForm(data={"tenant_code": "alpha"}, request=request)

        self.assertFalse(form.is_valid())
        self.assertIn("tenant_code", form.errors)
        self.assertIn("workspace lookup failed", form.errors["tenant_code"][0])


class TenantContextTests(SimpleTestCase):
    @patch("nepanest.platform.tenancy.context.Tenant.objects")
    def test_tenant_lookup_errors_are_normalized(self, mocked_objects):
        mocked_objects.using.return_value.filter.return_value.first.side_effect = DatabaseError("table missing")

        with self.assertRaises(TenantLookupError):
            resolve_tenant_by_code("alpha")


class TenantResolutionMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        clear_current_tenant()

    @override_settings(DATABASES={"default": {}, "tenant_alpha": {}})
    def test_middleware_restores_tenant_from_session(self):
        request = self.factory.get("/")
        request.session = {"tenant_code": "alpha"}

        seen = {}

        def get_response(incoming_request):
            seen["tenant_code"] = getattr(incoming_request, "tenant_code", None)
            seen["database_alias"] = getattr(incoming_request, "tenant_database_alias", None)
            return SimpleNamespace(status_code=200)

        fake_tenant = SimpleNamespace(code="alpha", database_alias="tenant_alpha")

        with patch("nepanest.platform.tenancy.middleware.resolve_tenant_by_code", return_value=fake_tenant):
            middleware = TenantResolutionMiddleware(get_response)
            response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(seen["tenant_code"], "alpha")
        self.assertEqual(seen["database_alias"], "tenant_alpha")

    @patch("nepanest.platform.tenancy.middleware.resolve_tenant_by_code", side_effect=TenantLookupError("workspace lookup failed"))
    def test_middleware_fails_open_when_tenant_lookup_is_unavailable(self, _mocked_lookup):
        request = self.factory.get("/")
        request.session = {"tenant_code": "alpha"}

        seen = {}

        def get_response(incoming_request):
            seen["tenant_code"] = getattr(incoming_request, "tenant_code", "set")
            seen["database_alias"] = getattr(incoming_request, "tenant_database_alias", "set")
            return SimpleNamespace(status_code=200)

        middleware = TenantResolutionMiddleware(get_response)
        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(seen["tenant_code"])
        self.assertIsNone(seen["database_alias"])

    @patch("nepanest.platform.tenancy.middleware.resolve_tenant_by_code")
    def test_registry_paths_skip_tenant_resolution(self, mocked_resolve):
        request = self.factory.get("/registry/")
        request.session = {"tenant_code": "alpha"}

        seen = {}

        def get_response(incoming_request):
            seen["tenant_code"] = getattr(incoming_request, "tenant_code", None)
            seen["database_alias"] = getattr(incoming_request, "tenant_database_alias", None)
            return SimpleNamespace(status_code=200)

        middleware = TenantResolutionMiddleware(get_response)
        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(seen["tenant_code"])
        self.assertIsNone(seen["database_alias"])
        mocked_resolve.assert_not_called()


class TenantDatabaseRouterTests(SimpleTestCase):
    def tearDown(self):
        clear_current_tenant()

    @override_settings(DATABASES={"default": {}, "tenant_alpha": {}})
    def test_router_uses_current_tenant_database_for_business_models(self):
        set_current_tenant(SimpleNamespace(code="alpha", database_alias="tenant_alpha"))
        router = TenantDatabaseRouter()
        model = SimpleNamespace(_meta=SimpleNamespace(app_label="accounting"))

        self.assertEqual(router.db_for_read(model), "tenant_alpha")
        self.assertEqual(router.db_for_write(model), "tenant_alpha")

    @override_settings(DATABASES={"default": {}, "tenant_alpha": {}})
    def test_router_keeps_shared_apps_on_default_database(self):
        set_current_tenant(SimpleNamespace(code="alpha", database_alias="tenant_alpha"))
        router = TenantDatabaseRouter()
        model = SimpleNamespace(_meta=SimpleNamespace(app_label="sessions"))

        self.assertEqual(router.db_for_read(model), "default")
        self.assertEqual(router.db_for_write(model), "default")

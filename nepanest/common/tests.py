from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from nepanest.common.middlewares.tenant_middleware import TenantDatabaseMiddleware
from nepanest.common.utils.tenant_db import clear_current_db


class TenantDatabaseMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        clear_current_db()

    def test_exempt_path_skips_auth_enforcement_but_still_reaches_view(self):
        request = self.factory.get("/accounts/login/")
        request.session = {}
        request.user = SimpleNamespace(is_authenticated=False)

        seen = {}

        def get_response(incoming_request):
            seen["db_alias"] = getattr(incoming_request, "db_alias", None)
            seen["tenant_code"] = getattr(incoming_request, "tenant_code", None)
            return SimpleNamespace(status_code=200)

        response = TenantDatabaseMiddleware(get_response)(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(seen["db_alias"], "default")
        self.assertIsNone(seen["tenant_code"])

    def test_registry_login_path_bypasses_tenant_enforcement(self):
        request = self.factory.get("/registry/login/")
        request.session = {}
        request.user = SimpleNamespace(is_authenticated=False)

        seen = {}

        def get_response(incoming_request):
            seen["db_alias"] = getattr(incoming_request, "db_alias", None)
            seen["tenant_code"] = getattr(incoming_request, "tenant_code", None)
            return SimpleNamespace(status_code=200)

        response = TenantDatabaseMiddleware(get_response)(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(seen["db_alias"], "default")
        self.assertIsNone(seen["tenant_code"])

    @patch("nepanest.common.utils.tenant_db.get_tenant_db_alias", return_value="tenant_alpha")
    def test_non_exempt_request_uses_tenant_session_code(self, _mocked_lookup):
        request = self.factory.get("/core/dashboard/")
        request.session = {"tenant_code": "alpha"}
        request.user = SimpleNamespace(is_authenticated=True)

        seen = {}

        def get_response(incoming_request):
            seen["db_alias"] = getattr(incoming_request, "db_alias", None)
            seen["gym_code"] = getattr(incoming_request, "gym_code", None)
            seen["tenant_code"] = getattr(incoming_request, "tenant_code", None)
            return SimpleNamespace(status_code=200)

        response = TenantDatabaseMiddleware(get_response)(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(seen["db_alias"], "tenant_alpha")
        self.assertEqual(seen["gym_code"], "alpha")
        self.assertEqual(seen["tenant_code"], "alpha")

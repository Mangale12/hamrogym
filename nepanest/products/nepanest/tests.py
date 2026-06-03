from types import SimpleNamespace

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve, reverse

from nepanest.products.nepanest.views import views


class PlatformURLTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(ROOT_URLCONF="config.urls")
    def test_platform_dashboard_reverse(self):
        self.assertEqual(reverse("platform_dashboard"), "/platform/dashboard/")

    @override_settings(ROOT_URLCONF="config.urls")
    def test_platform_dashboard_resolves_to_dashboard_view(self):
        match = resolve("/platform/dashboard/")
        self.assertIs(match.func, views.dashboard)

    def test_platform_dashboard_view_uses_platform_template(self):
        request = self.factory.get("/platform/dashboard/")
        request.user = SimpleNamespace(is_authenticated=True)
        response = views.dashboard(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform Dashboard")

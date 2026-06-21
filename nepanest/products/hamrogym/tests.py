from pathlib import Path

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import resolve, reverse

from nepanest.common.middlewares.host_routing import HostURLConfMiddleware
from nepanest.products.hamrogym.context_processors import base_layout_template
from nepanest.products.hamrogym.views import views


class HostURLConfMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(
        HOST_URLCONF_MAP={"nepanest.local": "config.urlconfs.nepanest"},
        PRODUCT_SUBDOMAIN_BASE_DOMAIN="nepanest.local",
        PRODUCT_SUBDOMAIN_URLCONFS={"hamrogym": "config.urls"},
    )
    def test_exact_host_uses_matching_urlconf(self):
        seen = {}

        def get_response(request):
            seen["urlconf"] = getattr(request, "urlconf", None)
            return HttpResponse("ok")

        middleware = HostURLConfMiddleware(get_response)
        request = self.factory.get("/", HTTP_HOST="nepanest.local")

        middleware(request)

        self.assertEqual(seen["urlconf"], "config.urlconfs.nepanest")

    @override_settings(
        HOST_URLCONF_MAP={},
        PRODUCT_SUBDOMAIN_BASE_DOMAIN="nepanest.local",
        PRODUCT_SUBDOMAIN_URLCONFS={"hamrogym": "config.urls"},
    )
    def test_product_subdomain_uses_matching_urlconf(self):
        seen = {}

        def get_response(request):
            seen["urlconf"] = getattr(request, "urlconf", None)
            return HttpResponse("ok")

        middleware = HostURLConfMiddleware(get_response)
        request = self.factory.get("/", HTTP_HOST="hamrogym.nepanest.local")

        middleware(request)

        self.assertEqual(seen["urlconf"], "config.urls")

    @override_settings(
        HOST_URLCONF_MAP={},
        PRODUCT_SUBDOMAIN_BASE_DOMAIN="nepanest.local",
        PRODUCT_SUBDOMAIN_URLCONFS={},
    )
    def test_unmapped_host_keeps_default_urlconf(self):
        seen = {}

        def get_response(request):
            seen["urlconf"] = getattr(request, "urlconf", None)
            return HttpResponse("ok")

        middleware = HostURLConfMiddleware(get_response)
        request = self.factory.get("/", HTTP_HOST="unknown.local")

        middleware(request)

        self.assertIsNone(seen["urlconf"])


class HamroGymURLTests(SimpleTestCase):
    @override_settings(ROOT_URLCONF="config.urls")
    def test_dashboard_route_uses_trailing_slash(self):
        self.assertEqual(reverse("dashboard"), "/product/hamrogym/dashboard/")

    @override_settings(ROOT_URLCONF="config.urls")
    def test_dashboard_url_resolves_to_dashboard_view(self):
        match = resolve("/product/hamrogym/dashboard/")
        self.assertIs(match.func, views.dashboard)


class HamroGymTemplateTests(SimpleTestCase):
    def test_dashboard_template_uses_hamrogym_layout_namespace(self):
        template_path = Path(__file__).resolve().parent / "templates" / "hamrogym" / "dashboard.html"
        self.assertIn('{% extends "hamrogym/layouts/app.html" %}', template_path.read_text())

    def test_hamrogym_layout_namespace_template_exists(self):
        layout_path = Path(__file__).resolve().parent / "templates" / "hamrogym" / "layouts" / "app.html"
        self.assertTrue(layout_path.exists())

    def test_hamrogym_layout_uses_product_sidebar_tag(self):
        layout_path = Path(__file__).resolve().parent / "templates" / "hamrogym" / "layouts" / "app.html"
        self.assertIn("{% render_hamrogym_sidebar %}", layout_path.read_text())


class LayoutResolverTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_platform_path_uses_platform_layout(self):
        request = self.factory.get("/platform/dashboard/")

        context = base_layout_template(request)

        self.assertEqual(context["base_layout_template"], "platform/layouts/app.html")

    def test_regular_product_path_uses_hamrogym_layout(self):
        request = self.factory.get("/product/hamrogym/dashboard/")

        context = base_layout_template(request)

        self.assertEqual(context["base_layout_template"], "layouts/shared_app.html")

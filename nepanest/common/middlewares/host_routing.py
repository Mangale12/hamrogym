from django.conf import settings


class HostURLConfMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":", 1)[0].lower()

        urlconf = getattr(settings, "HOST_URLCONF_MAP", {}).get(host)
        if urlconf is None:
            base_domain = getattr(settings, "PRODUCT_SUBDOMAIN_BASE_DOMAIN", "").strip().lower()
            if base_domain and host.endswith(f".{base_domain}"):
                subdomain = host[: -(len(base_domain) + 1)]
                urlconf = getattr(settings, "PRODUCT_SUBDOMAIN_URLCONFS", {}).get(subdomain)

        if urlconf:
            request.urlconf = urlconf

        return self.get_response(request)

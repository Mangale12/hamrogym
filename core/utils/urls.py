from django.urls import reverse, NoReverseMatch


def reverse_with_request(url_name: str, request=None, args=None, kwargs=None) -> str:
    """
    Attempt to reverse a URL using the current request's resolver namespace
    (if present). Fall back to the un-namespaced reverse if namespaced lookup
    fails. Returns '#' if reversal fails.
    """
    args = args or []
    kwargs = kwargs or {}
    if request and getattr(request, "resolver_match", None):
        ns = request.resolver_match.namespace
        if ns:
            try:
                return reverse(f"{ns}:{url_name}", args=args, kwargs=kwargs)
            except NoReverseMatch:
                pass
    try:
        return reverse(url_name, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return "#"

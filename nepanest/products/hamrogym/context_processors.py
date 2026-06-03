def sidebar_items(request):
    return {"sidebar_items": []}


def _first_path_segment(request):
    path = ""
    if request:
        path = getattr(request, "path_info", "") or getattr(request, "path", "") or ""

    return path.lstrip("/").split("/", 1)[0].lower()


def base_layout_template(request):
    host = ""
    if request:
        host = (request.get_host() or "").split(":", 1)[0].lower()

    first_segment = _first_path_segment(request)
    urlconf = getattr(request, "urlconf", "") or ""
    is_platform_route = first_segment == "platform"
    is_nepanest = host == "nepanest.local" or urlconf == "config.urlconfs.nepanest"

    if is_platform_route:
        base_layout = "platform/layouts/app.html"
    elif is_nepanest:
        base_layout = "layouts/shared_app.html"
    else:
        base_layout = "hamrogym/layouts/app.html"

    return {
        "base_layout_template": base_layout,
    }

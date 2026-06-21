def sidebar_items(request):
    return {"sidebar_items": []}


def _first_path_segment(request):
    path = ""
    if request:
        path = getattr(request, "path_info", "") or getattr(request, "path", "") or ""

    return path.lstrip("/").split("/", 1)[0].lower()


def base_layout_template(request):
    first_segment = _first_path_segment(request)
    if first_segment == "platform":
        base_layout = "platform/layouts/app.html"
    else:
        base_layout = "layouts/shared_app.html"

    return {
        "base_layout_template": base_layout,
    }

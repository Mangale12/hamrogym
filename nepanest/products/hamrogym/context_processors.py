def sidebar_items(request):
    return {"sidebar_items": []}


def base_layout_template(request):
    host = ""
    if request:
        host = (request.get_host() or "").split(":", 1)[0].lower()

    urlconf = getattr(request, "urlconf", "") or ""
    is_nepanest = host == "nepanest.local" or urlconf == "config.urlconfs.nepanest"

    return {
        "base_layout_template": (
            "layouts/shared_app.html" if is_nepanest else "hamrogym/layouts/app.html"
        )
    }

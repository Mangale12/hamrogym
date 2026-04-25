from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse


@login_required
def user_select(request):
    term = (request.GET.get("term") or request.GET.get("q") or "").strip()
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 20))
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100

    queryset = User.objects.all()
    if term:
        queries = (
            Q(username__icontains=term)
            | Q(email__icontains=term)
            | Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
        )
        queryset = queryset.filter(queries)

    start = (page - 1) * page_size
    items = list(queryset.order_by("username")[start : start + page_size + 1])
    more = len(items) > page_size
    items = items[:page_size]

    results = [
        {
            "id": obj.pk,
            "text": obj.get_full_name() or obj.username,
        }
        for obj in items
    ]
    return JsonResponse({"results": results, "pagination": {"more": more}})

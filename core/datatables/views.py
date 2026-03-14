from django.db.models import Q
from django.http import JsonResponse
from django.views import View


class BaseDataTableView(View):
    model = None
    columns = []  # list of (key, accessor) where accessor is str or callable
    searchable_columns = []  # list of model field names
    orderable_columns = []  # list of model field names

    def get_queryset(self):
        if not self.model:
            raise NotImplementedError("model is required")
        return self.model.objects.all()

    def filter_queryset(self, queryset, search_value):
        if not search_value:
            return queryset
        queries = Q()
        for column in self.searchable_columns:
            queries |= Q(**{f"{column}__icontains": search_value})
        return queryset.filter(queries)

    def order_queryset(self, queryset, order_index, order_dir):
        if order_index < len(self.orderable_columns):
            column_name = self.orderable_columns[order_index]
            if order_dir == "desc":
                column_name = f"-{column_name}"
            return queryset.order_by(column_name)
        return queryset

    def serialize_row(self, obj):
        row = {}
        for key, accessor in self.columns:
            if callable(accessor):
                row[key] = accessor(obj)
            else:
                value = obj
                for part in accessor.split("."):
                    value = getattr(value, part, None)
                row[key] = value
        return row

    def get(self, request, *args, **kwargs):
        draw = int(request.GET.get("draw", 1))
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))
        search_value = request.GET.get("search[value]", "")
        order_index = int(request.GET.get("order[0][column]", 0))
        order_dir = request.GET.get("order[0][dir]", "asc")
        first_column = request.GET.get("columns[0][data]", "")
        if first_column == "__sno__":
            if order_index > 0:
                order_index -= 1
            else:
                order_index = 0

        queryset = self.get_queryset()
        total_records = queryset.count()

        queryset = self.filter_queryset(queryset, search_value)
        filtered_records = queryset.count()

        queryset = self.order_queryset(queryset, order_index, order_dir)

        page = queryset[start : start + length]
        data = [self.serialize_row(obj) for obj in page]

        return JsonResponse(
            {
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": filtered_records,
                "data": data,
            }
        )

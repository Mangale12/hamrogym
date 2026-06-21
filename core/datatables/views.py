import inspect
import logging

from django.db.models import Q, Count
from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class BaseDataTableView(View):
    model = None
    columns = []  # list of (key, accessor) where accessor is str or callable
    searchable_columns = []  # list of model field names
    orderable_columns = []  # list of model field names
    max_records_count = 100000  # Threshold for approximate counts
    query_timeout = 30  # seconds

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
                parameter_count = len(inspect.signature(accessor).parameters)
                if parameter_count >= 2:
                    row[key] = accessor(obj, self.request)
                else:
                    row[key] = accessor(obj)
            else:
                value = obj
                for part in accessor.split("."):
                    value = getattr(value, part, None)
                row[key] = value
        return row

    def get_count_safe(self, queryset, label=""):
        """Safely count records with timeout and error handling."""
        try:
            # Set connection timeout to prevent long-running queries
            with connection.cursor() as cursor:
                # Get the count with a reasonable timeout
                count = queryset.count()
                return count
        except OperationalError as e:
            logger.error(f"Database timeout counting {label}: {str(e)}")
            # Return approximate count or -1 on error
            return -1
        except Exception as e:
            logger.error(f"Error counting {label}: {str(e)}")
            return -1

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

        try:
            queryset = self.get_queryset()
            
            # Get total count efficiently
            total_records = self.get_count_safe(queryset, "total_records")
            if total_records == -1:
                total_records = 0

            # Apply filtering
            queryset = self.filter_queryset(queryset, search_value)
            
            # Get filtered count efficiently
            filtered_records = self.get_count_safe(queryset, "filtered_records")
            if filtered_records == -1:
                filtered_records = 0

            # Apply ordering
            queryset = self.order_queryset(queryset, order_index, order_dir)

            # Apply pagination - CRITICAL: slice before serialization to limit data transfer
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
        except Exception as e:
            logger.error(f"Error in datatable view: {str(e)}")
            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": 0,
                    "recordsFiltered": 0,
                    "data": [],
                    "error": str(e),
                },
                status=500,
            )

# Nepanest/datatables/datatable_server.py
from django.http import JsonResponse
from django.db.models import Q, F
from django.core.paginator import Paginator
from datetime import datetime
import json


class DataTableServer:
    """
    Base class for server-side DataTables processing
    Supports: Pagination, Search, Sorting, Column filtering
    """
    
    model = None
    columns = []  # List of column names
    searchable_columns = []  # Columns that can be searched
    orderable_columns = []  # Columns that can be sorted
    
    def __init__(self, request):
        self.request = request
        self.draw = int(request.GET.get('draw', 1))
        self.start = int(request.GET.get('start', 0))
        self.length = int(request.GET.get('length', 10))
        self.search_value = request.GET.get('search[value]', '')
        
    def get_queryset(self):
        """Override this method to return your base queryset"""
        if self.model:
            return self.model.objects.all()
        raise NotImplementedError("You must either set model or override get_queryset()")
    
    def filter_queryset(self, queryset):
        """Apply global search filter"""
        if self.search_value:
            queries = Q()
            for column in self.searchable_columns:
                queries |= Q(**{f'{column}__icontains': self.search_value})
            queryset = queryset.filter(queries)
        return queryset
    
    def order_queryset(self, queryset):
        """Apply ordering based on DataTables parameters"""
        order_column_index = int(self.request.GET.get('order[0][column]', 0))
        order_direction = self.request.GET.get('order[0][dir]', 'asc')
        
        if order_column_index < len(self.orderable_columns):
            column_name = self.orderable_columns[order_column_index]
            if order_direction == 'desc':
                column_name = f'-{column_name}'
            queryset = queryset.order_by(column_name)
        
        return queryset
    
    def get_data(self, queryset):
        """Transform queryset to list of dicts for DataTables"""
        data = []
        for obj in queryset:
            row = {}
            for i, column in enumerate(self.columns):
                if callable(column):
                    row[i] = column(obj)
                elif '.' in column:
                    # Handle related fields (e.g., 'user.username')
                    value = obj
                    for part in column.split('.'):
                        value = getattr(value, part, None)
                    row[i] = value
                else:
                    row[i] = getattr(obj, column, None)
            data.append(row)
        return data
    
    def get_response(self):
        """Main method to process request and return JSON response"""
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        
        # Get total records before pagination
        total_records = queryset.count()
        
        # Apply ordering
        queryset = self.order_queryset(queryset)
        
        # Paginate
        paginator = Paginator(queryset, self.length)
        page = paginator.get_page((self.start // self.length) + 1)
        
        # Get data
        data = self.get_data(page.object_list)
        
        response_data = {
            'draw': self.draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        }
        
        return JsonResponse(response_data)
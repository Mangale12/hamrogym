from __future__ import annotations

from datetime import date
from typing import Dict, List, Type

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from core.config import EntityConfig


def _serialize_form_instance(form) -> Dict[str, object]:
    data = {}
    instance = form.instance
    for name, field in form.fields.items():
        if hasattr(instance, name):
            value = getattr(instance, name, None)
        elif name in form.initial:
            value = form.initial.get(name)
        else:
            value = field.initial
        value = field.prepare_value(value)
        if isinstance(value, date):
            value = value.strftime("%Y-%m-%d")
        data[name] = value
    return data


def _actions_render(entity: EntityConfig) -> str:
    detail_url = reverse(f"{entity.name}_detail", args=[0]).replace("/0/", "/{id}/")
    update_url = reverse(f"{entity.name}_update", args=[0]).replace("/0/", "/{id}/")
    delete_url = reverse(f"{entity.name}_delete", args=[0]).replace("/0/", "/{id}/")

    return (
        "function(id){return renderActionButtons(id, {"
        f"edit: '{update_url}', "
        f"delete: '{delete_url}', "
        f"detail: '{detail_url}', "
        f"modal_id: '#{entity.name}Modal', "
        f"title: 'Edit {entity.verbose_name}'"
        "});}"
    )


def _build_select_queryset(entity: EntityConfig, term: str):
    queryset = entity.model.objects.all()
    if not term:
        return queryset
    queries = Q()
    for field in entity.get_select_search_fields():
        queries |= Q(**{f"{field}__icontains": term})
    return queryset.filter(queries)


def _resolve_field_urls(fields: List[Dict[str, object]]) -> List[Dict[str, object]]:
    resolved = []
    for raw in fields or []:
        field = dict(raw)
        url_name = field.get("url_name")
        if url_name and not field.get("url"):
            field["url"] = reverse(url_name)
        resolved.append(field)
    return resolved


def build_entity_views(entity: EntityConfig) -> Dict[str, Type[View]]:
    class EntityListView(LoginRequiredMixin, TemplateView):
        template_name = entity.template_name

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            fields = _resolve_field_urls(entity.fields)
            tabs = None
            if entity.tabs:
                resolved_tabs = []
                for tab in entity.tabs:
                    tab_data = dict(tab)
                    tab_data["fields"] = _resolve_field_urls(tab_data.get("fields", []))
                    section_names = tab_data.get("sections") or tab_data.get("section_names") or []
                    if section_names and entity.dynamic_sections:
                        tab_data["sections"] = [
                            {"name": name, "section": entity.dynamic_sections.get(name)}
                            for name in section_names
                            if entity.dynamic_sections.get(name)
                        ]
                    else:
                        tab_data["sections"] = []
                    resolved_tabs.append(tab_data)
                tabs = resolved_tabs
            context.update(
                {
                    "entity_name": entity.name,
                    "entity_label": entity.verbose_name,
                    "modal_id": f"{entity.name}Modal",
                    "form_id": f"{entity.name}Form",
                    "table_id": f"{entity.name}Table",
                    "table_var": None,
                    "fields": fields,
                    "tabs": tabs,
                    "dynamic_sections": entity.dynamic_sections or {},
                    "datatable_url": reverse(f"{entity.name}_datatable"),
                    "create_url": reverse(f"{entity.name}_create"),
                    "update_url_template": reverse(f"{entity.name}_update", args=[0]).replace(
                        "/0/", "/{id}/"
                    ),
                    "detail_url_template": reverse(f"{entity.name}_detail", args=[0]).replace(
                        "/0/", "/{id}/"
                    ),
                    "delete_url_template": reverse(f"{entity.name}_delete", args=[0]).replace(
                        "/0/", "/{id}/"
                    ),
                    "modal_title_add": f"Add {entity.verbose_name}",
                    "modal_title_edit": f"Edit {entity.verbose_name}",
                    "reset_defaults": entity.reset_defaults,
                }
            )

            context["datatable_columns"] = entity.datatable_columns + [
                {
                    "name": "id",
                    "title": "Actions",
                    "orderable": False,
                    "searchable": False,
                    "render": _actions_render(entity),
                }
            ]
            return context

    class EntityDetailView(LoginRequiredMixin, View):
        def get(self, request, pk):
            obj = get_object_or_404(entity.model, pk=pk)
            form = entity.form_class(instance=obj)
            data = _serialize_form_instance(form)
            data["id"] = obj.pk
            if entity.dynamic_sections_loader:
                data["__dynamic_sections__"] = entity.dynamic_sections_loader(obj)
            return JsonResponse({"success": True, "data": data})

    class EntityCreateView(LoginRequiredMixin, View):
        def post(self, request):
            form = entity.form_class(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                if hasattr(obj, "created_by_id"):
                    obj.created_by = request.user
                if hasattr(obj, "updated_by_id"):
                    obj.updated_by = request.user
                obj.save()
                if hasattr(form, "save_m2m"):
                    form.save_m2m()
                if entity.dynamic_sections_saver:
                    entity.dynamic_sections_saver(request, obj)
                if entity.post_save:
                    entity.post_save(request, obj)
                return JsonResponse({"success": True, "id": obj.pk})
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    class EntityUpdateView(LoginRequiredMixin, View):
        def post(self, request, pk):
            obj = get_object_or_404(entity.model, pk=pk)
            form = entity.form_class(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                obj = form.save(commit=False)
                if hasattr(obj, "updated_by_id"):
                    obj.updated_by = request.user
                obj.save()
                if hasattr(form, "save_m2m"):
                    form.save_m2m()
                if entity.dynamic_sections_saver:
                    entity.dynamic_sections_saver(request, obj)
                if entity.post_save:
                    entity.post_save(request, obj)
                return JsonResponse({"success": True, "id": obj.pk})
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    class EntityDeleteView(LoginRequiredMixin, View):
        def post(self, request, pk):
            obj = get_object_or_404(entity.model, pk=pk)
            obj.delete()
            return JsonResponse({"success": True})

    class EntitySelectView(LoginRequiredMixin, View):
        def get(self, request):
            term = (request.GET.get("term") or request.GET.get("q") or "").strip()
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", entity.select_page_size or 20))
            if page < 1:
                page = 1
            if page_size < 1:
                page_size = 20
            if page_size > 100:
                page_size = 100

            ids_param = (request.GET.get("ids") or request.GET.get("id") or "").strip()
            if ids_param:
                ids = [int(val) for val in ids_param.split(",") if val.strip().isdigit()]
                queryset = entity.model.objects.filter(pk__in=ids)
                items = list(queryset)
                results = [
                    {"id": obj.pk, "text": entity.get_select_label(obj)}
                    for obj in items
                ]
                return JsonResponse({"results": results, "pagination": {"more": False}})

            queryset = _build_select_queryset(entity, term).order_by(entity.get_select_order_by())
            start = (page - 1) * page_size
            items = list(queryset[start : start + page_size + 1])
            more = len(items) > page_size
            items = items[:page_size]
            results = [
                {"id": obj.pk, "text": entity.get_select_label(obj)}
                for obj in items
            ]
            return JsonResponse({"results": results, "pagination": {"more": more}})

    data_table_view = type(
        f"{entity.name.title().replace('_', '')}DataTableView",
        (LoginRequiredMixin, entity.datatable_view),
        {},
    )

    return {
        "list_view": EntityListView,
        "detail_view": EntityDetailView,
        "create_view": EntityCreateView,
        "update_view": EntityUpdateView,
        "delete_view": EntityDeleteView,
        "datatable_view": data_table_view,
        "select_view": EntitySelectView,
    }

from __future__ import annotations

from datetime import date
import inspect
import json
from typing import Dict, List, Type

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from core.config import EntityConfig
from core.helpers.helper import encode_date_for_display
from core.helpers.context import get_current_branch_id, get_current_fiscal_year_id


def _serialize_value(value, request=None):
    if isinstance(value, File):
        return value.name if value else ""
    if isinstance(value, date):
        return encode_date_for_display(value, request)
    if isinstance(value, dict):
        return {key: _serialize_value(item, request) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_value(item, request) for item in value]
    return value


def _serialize_form_instance(form, request=None) -> Dict[str, object]:
    data = {}
    instance = form.instance
    for name, field in form.fields.items():
        if hasattr(instance, name):
            value = getattr(instance, name, None)
            if value in (None, ""):
                if name in form.initial:
                    value = form.initial.get(name)
                elif field.initial not in (None, ""):
                    value = field.initial
        elif name in form.initial:
            value = form.initial.get(name)
        else:
            value = field.initial
        if isinstance(value, File):
            value = value.name if value else ""
        if isinstance(value, date):
            value = encode_date_for_display(value, request)
        else:
            value = field.prepare_value(value)
        data[name] = _serialize_value(value, request)
    return data


def _load_dynamic_sections_data(entity: EntityConfig, obj, request):
    if not entity.dynamic_sections_loader:
        return None

    loader = entity.dynamic_sections_loader
    try:
        parameters = inspect.signature(loader).parameters
        if len(parameters) >= 2:
            return loader(obj, request)
    except (TypeError, ValueError):
        pass
    return loader(obj)


def _build_entity_form(entity: EntityConfig, *args, request=None, **kwargs):
    try:
        return entity.form_class(*args, request=request, **kwargs)
    except TypeError:
        return entity.form_class(*args, **kwargs)


def _actions_render(entity: EntityConfig) -> str:
    detail_url = reverse(f"{entity.name}_detail", args=[0]).replace("/0/", "/{id}/")
    update_url = reverse(f"{entity.name}_update", args=[0]).replace("/0/", "/{id}/")
    delete_url = reverse(f"{entity.name}_delete", args=[0]).replace("/0/", "/{id}/")
    resolved_actions = []
    for raw_action in entity.action_buttons or []:
        action = dict(raw_action)
        action_name = action.get("action_name")
        if action_name and action_name in (entity.row_actions or {}):
            action["action_url"] = reverse(f"{entity.name}_{action_name}", args=[0]).replace(
                "/0/", "/{id}/"
            )
        resolved_actions.append(action)
    extra_actions = json.dumps(resolved_actions)

    return (
        "function(data,type,row){return renderActionButtons((row && row.id) || data, {"
        f"view: {'true' if entity.show_view else 'false'}, "
        f"edit: '{update_url}', "
        f"delete: '{delete_url}', "
        f"detail: '{detail_url}', "
        f"modal_id: '#{entity.name}Modal', "
        f"title: 'Edit {entity.verbose_name}', "
        f"view_title: 'View {entity.verbose_name}', "
        f"action_state_field: {json.dumps(entity.action_state_field)}, "
        f"hide_edit_on_values: {json.dumps(entity.hide_edit_on_values)}, "
        f"hide_delete_on_values: {json.dumps(entity.hide_delete_on_values)}, "
        f"extra_actions: {extra_actions}"
        "}, row || {});}"
    )


def _build_select_queryset(entity: EntityConfig, term: str):
    queryset = entity.model.objects.all()
    if not term:
        return queryset
    queries = Q()
    for field in entity.get_select_search_fields():
        queries |= Q(**{f"{field}__icontains": term})
    return queryset.filter(queries)


def _resolve_field_urls(fields: List[Dict[str, object]], request=None) -> List[Dict[str, object]]:
    resolved = []
    for raw in fields or []:
        field = dict(raw)
        url_name = field.get("url_name")
        if url_name and not field.get("url"):
            field["url"] = reverse(url_name)
        options = field.get("options")
        if callable(options):
            try:
                field["options"] = options(request)
            except TypeError:
                field["options"] = options()
        resolved.append(field)
    return resolved


def _resolve_dynamic_sections(sections: Dict[str, object], request=None) -> Dict[str, object]:
    resolved_sections = {}
    for section_name, raw_section in (sections or {}).items():
        section = dict(raw_section)
        section["fields"] = _resolve_field_urls(section.get("fields", []), request)
        resolved_sections[section_name] = section
    return resolved_sections


def _assign_context_defaults(request, obj, form) -> None:
    if hasattr(obj, "fiscal_year_id") and not getattr(obj, "fiscal_year_id", None):
        fiscal_year_id = get_current_fiscal_year_id(request)
        if fiscal_year_id:
            obj.fiscal_year_id = fiscal_year_id
        else:
            error_field = "fiscal_year" if "fiscal_year" in form.fields else None
            form.add_error(error_field, "Active fiscal year not found in session.")
    if hasattr(obj, "branch_id") and not getattr(obj, "branch_id", None):
        branch_id = get_current_branch_id(request)
        if branch_id:
            obj.branch_id = branch_id
        else:
            error_field = "branch" if "branch" in form.fields else None
            form.add_error(error_field, "Active branch not found in session.")


def build_entity_views(entity: EntityConfig) -> Dict[str, Type[View]]:
    class EntityListView(LoginRequiredMixin, TemplateView):
        template_name = entity.template_name

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            fields = _resolve_field_urls(entity.fields, self.request)
            dynamic_sections = _resolve_dynamic_sections(entity.dynamic_sections or {}, self.request)
            singleton_object = None
            singleton_form_data = None
            tabs = None
            if entity.tabs:
                resolved_tabs = []
                for tab in entity.tabs:
                    tab_data = dict(tab)
                    tab_data["fields"] = _resolve_field_urls(tab_data.get("fields", []), self.request)
                    section_names = tab_data.get("sections") or tab_data.get("section_names") or []
                    if section_names and dynamic_sections:
                        tab_data["sections"] = [
                            {"name": name, "section": dynamic_sections.get(name)}
                            for name in section_names
                            if dynamic_sections.get(name)
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
                    "dynamic_sections": dynamic_sections,
                    "dynamic_section_entries": list(dynamic_sections.items()),
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
                    "modal_title_view": f"View {entity.verbose_name}",
                    "reset_defaults": _serialize_value(
                        {
                            **_serialize_form_instance(_build_entity_form(entity, request=self.request), self.request),
                            **(entity.reset_defaults or {}),
                        },
                        self.request,
                    ),
                    "show_create": entity.show_create,
                    "is_singleton": entity.singleton,
                }
            )

            if entity.singleton:
                singleton_object = entity.model.objects.first()
                if singleton_object:
                    singleton_form_data = _serialize_form_instance(
                        _build_entity_form(entity, instance=singleton_object, request=self.request),
                        self.request,
                    )
                else:
                    singleton_form_data = dict(entity.reset_defaults or {})
                context.update(
                    {
                        "singleton_object": singleton_object,
                        "singleton_form_data": singleton_form_data or {},
                        "singleton_save_url": (
                            reverse(f"{entity.name}_update", args=[singleton_object.pk])
                            if singleton_object
                            else reverse(f"{entity.name}_create")
                        ),
                    }
                )

            context["datatable_columns"] = list(entity.datatable_columns)
            if entity.show_actions:
                context["datatable_columns"].append(
                    {
                        "name": "id",
                        "title": "Actions",
                        "orderable": False,
                        "searchable": False,
                        "render": _actions_render(entity),
                    }
                )
            return context

    class EntityDetailView(LoginRequiredMixin, View):
        def get(self, request, pk):
            obj = get_object_or_404(entity.model, pk=pk)
            form = _build_entity_form(entity, instance=obj, request=request)
            data = _serialize_form_instance(form, request)
            data["id"] = obj.pk
            dynamic_sections_data = _load_dynamic_sections_data(entity, obj, request)
            if dynamic_sections_data is not None:
                data["__dynamic_sections__"] = dynamic_sections_data
            return JsonResponse({"success": True, "data": data})

    class EntityCreateView(LoginRequiredMixin, View):
        def post(self, request):
            instance = entity.model.objects.first() if entity.singleton else None
            form = _build_entity_form(entity, request.POST, request.FILES, instance=instance, request=request)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        obj = form.save(commit=False)
                        _assign_context_defaults(request, obj, form)
                        if form.errors:
                            return JsonResponse({"success": False, "errors": form.errors}, status=400)
                        if hasattr(obj, "created_by_id"):
                            obj.created_by = request.user
                        if hasattr(obj, "updated_by_id"):
                            obj.updated_by = request.user
                        if entity.pre_save:
                            entity.pre_save(request, obj)
                        obj.save()
                        if hasattr(form, "save_m2m"):
                            form.save_m2m()
                        if entity.dynamic_sections_saver:
                            entity.dynamic_sections_saver(request, obj)
                        if entity.post_save:
                            entity.post_save(request, obj)
                    return JsonResponse({"success": True, "id": obj.pk})
                except ValidationError as exc:
                    return JsonResponse({"success": False, "errors": exc.message_dict if hasattr(exc, "message_dict") else {"__all__": exc.messages}}, status=400)
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    class EntityUpdateView(LoginRequiredMixin, View):
        def post(self, request, pk):
            obj = get_object_or_404(entity.model, pk=pk)
            form = _build_entity_form(entity, request.POST, request.FILES, instance=obj, request=request)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        obj = form.save(commit=False)
                        _assign_context_defaults(request, obj, form)
                        if form.errors:
                            return JsonResponse({"success": False, "errors": form.errors}, status=400)
                        if hasattr(obj, "updated_by_id"):
                            obj.updated_by = request.user
                        if entity.pre_save:
                            entity.pre_save(request, obj)
                        obj.save()
                        if hasattr(form, "save_m2m"):
                            form.save_m2m()
                        if entity.dynamic_sections_saver:
                            entity.dynamic_sections_saver(request, obj)
                        if entity.post_save:
                            entity.post_save(request, obj)
                    return JsonResponse({"success": True, "id": obj.pk})
                except ValidationError as exc:
                    return JsonResponse({"success": False, "errors": exc.message_dict if hasattr(exc, "message_dict") else {"__all__": exc.messages}}, status=400)
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    class EntityDeleteView(LoginRequiredMixin, View):
        def post(self, request, pk):
            if entity.singleton:
                return JsonResponse(
                    {"success": False, "message": f"{entity.verbose_name} cannot be deleted."},
                    status=405,
                )
            obj = get_object_or_404(entity.model, pk=pk)
            obj.delete()
            return JsonResponse({"success": True})

    action_views = {}
    for action_name, handler in (entity.row_actions or {}).items():
        def _build_action_view(_handler, _action_name):
            class EntityActionView(LoginRequiredMixin, View):
                def post(self, request, pk):
                    obj = get_object_or_404(entity.model, pk=pk)
                    try:
                        result = _handler(request, obj)
                        if isinstance(result, dict):
                            payload = {"success": True}
                            payload.update(result)
                            return JsonResponse(payload)
                        return JsonResponse(
                            {
                                "success": True,
                                "message": result or f"{entity.verbose_name} {_action_name} successful.",
                            }
                        )
                    except ValidationError as exc:
                        if hasattr(exc, "message_dict"):
                            errors = exc.message_dict
                            message = " ".join(
                                " ".join(messages) if isinstance(messages, list) else str(messages)
                                for messages in errors.values()
                            ).strip() or f"{entity.verbose_name} {_action_name} failed."
                            return JsonResponse(
                                {"success": False, "message": message, "errors": errors},
                                status=400,
                            )
                        messages = exc.messages if hasattr(exc, "messages") else [str(exc)]
                        message = " ".join(str(item) for item in messages if item).strip()
                        return JsonResponse(
                            {"success": False, "message": message or f"{entity.verbose_name} {_action_name} failed."},
                            status=400,
                        )

            return EntityActionView

        action_views[action_name] = _build_action_view(handler, action_name)

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
        "action_views": action_views,
    }

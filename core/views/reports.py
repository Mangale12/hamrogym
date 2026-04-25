import csv

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from nepanest.common.helpers.helper import decode_date_for_save, get_calendar_type


class BaseReportView(LoginRequiredMixin, TemplateView):
    template_name = "components/report/shared_report_datatable.html"
    form_class = None
    report_title = "Report"
    report_subtitle = ""
    report_table_id = "sharedReportTable"
    export_filename = "report"
    print_settings = {
        "page_size": "A4",
        "orientation": "portrait",
        "margin": "12mm",
        "summary_columns": 3,
    }
    filter_blocks = []
    filter_actions = [
        {
            "label": "View Report",
            "name": "generate",
            "value": "1",
            "class_name": "btn btn-primary",
            "icon_class": "fas fa-chart-line",
        }
    ]
    default_report_actions = [
        {
            "label": "Print",
            "kind": "button",
            "button_type": "button",
            "class_name": "btn btn-sm report-action-btn report-action-print",
            "icon_class": "fas fa-print",
            "data_attrs": {"report-print": "true"},
        },
        {
            "label": "Download Excel",
            "query_string": "format=excel",
            "kind": "link",
            "class_name": "btn btn-sm report-action-btn report-action-excel",
            "icon_class": "fas fa-download",
        },
        {
            "label": "Download Word",
            "query_string": "format=word",
            "kind": "link",
            "class_name": "btn btn-sm report-action-btn report-action-word",
            "icon_class": "fas fa-download",
        },
    ]
    report_actions = []

    def get_form_data(self):
        if not self.request.GET:
            return None

        data = self.request.GET.copy()
        requested_fields = set(data.getlist("__bs_date_fields"))
        if not requested_fields and get_calendar_type(self.request) != "BS":
            return data

        inspector_form = self.form_class()
        date_field_names = {
            name for name, field in inspector_form.fields.items() if isinstance(field, forms.DateField)
        }
        target_fields = requested_fields & date_field_names if requested_fields else date_field_names

        for field_name in target_fields:
            raw_value = (data.get(field_name) or "").strip()
            if not raw_value:
                continue
            try:
                converted = decode_date_for_save(raw_value, self.request)
                if hasattr(converted, "isoformat"):
                    converted = converted.isoformat()
                data[field_name] = converted
            except Exception:
                continue

        return data

    def get_form(self):
        if self.form_class is None:
            raise ValueError("form_class must be defined for BaseReportView subclasses.")
        return self.form_class(self.get_form_data())

    def should_generate(self, form) -> bool:
        return bool(self.request.GET.get("generate")) and form.is_valid()

    def get_export_format(self) -> str:
        return (self.request.GET.get("format") or "").strip().lower()

    def get_export_query(self) -> str:
        export_params = self.request.GET.copy()
        export_params.pop("format", None)
        return export_params.urlencode()

    def get_filter_blocks(self):
        return list(self.filter_blocks or [])

    def get_filter_actions(self):
        return list(self.filter_actions or [])

    def get_report_actions(self):
        return list(self.default_report_actions) + list(self.report_actions or [])

    def get_print_settings(self):
        settings = {
            "page_size": "A4",
            "orientation": "portrait",
            "margin": "12mm",
            "summary_columns": 3,
        }
        settings.update(self.print_settings or {})
        return settings

    def get_table_columns(self):
        return []

    def get_screen_columns(self):
        return list(self.get_table_columns())

    def get_print_columns(self):
        return list(self.get_table_columns())

    def get_export_columns(self):
        return list(self.get_table_columns())

    def get_table_rows(self, report_data):
        return list((report_data or {}).get("rows", []))

    def get_summary_cards(self, report_data):
        return []

    def get_screen_grid_columns(self, report_data):
        return [
            {"field": key, "headerName": label}
            for key, label in self.get_screen_columns()
        ]

    def get_screen_grid_rows(self, report_data):
        rows = []
        for row in self.get_table_rows(report_data):
            rows.append(
                {
                    key: self.normalize_export_value(row.get(key))
                    for key, _label in self.get_screen_columns()
                }
            )
        return rows

    def get_report_title(self, report_data=None):
        return (report_data or {}).get("report_title") or self.report_title

    def get_report_subtitle(self, report_data=None):
        if report_data:
            return self.report_subtitle or ""
        return self.report_subtitle or ""

    def build_report_data(self, cleaned_data):
        raise NotImplementedError

    def normalize_export_value(self, value):
        if isinstance(value, bool):
            return "Yes" if value else "No"
        if isinstance(value, dict):
            if "label" in value:
                return value.get("label") or ""
            if "value" in value:
                return value.get("value") or ""
        return "" if value is None else value

    def build_excel_response(self, report_data):
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = f'attachment; filename="{self.export_filename}.xls"'
        writer = csv.writer(response, delimiter="\t")
        columns = self.get_export_columns()
        writer.writerow([label for _key, label in columns])
        for row in self.get_table_rows(report_data):
            writer.writerow(
                [self.normalize_export_value(row.get(key)) for key, _label in columns]
            )
        return response

    def build_word_response(self, report_data):
        html = render_to_string(
            "components/report/report_export_word.html",
            {
                "report_title": self.get_report_title(report_data),
                "report_data": report_data,
                "table_columns": self.get_export_columns(),
            },
        )
        response = HttpResponse(content_type="application/msword")
        response["Content-Disposition"] = f'attachment; filename="{self.export_filename}.doc"'
        response.write(html)
        return response

    def build_export_response(self, report_data, export_format: str):
        if export_format == "excel":
            return self.build_excel_response(report_data)
        if export_format == "word":
            return self.build_word_response(report_data)
        return None

    def get_report_context(self, *, form, report_data, export_query):
        return {
            "page_title": self.get_report_title(report_data),
            "report_title": self.get_report_title(report_data),
            "report_subtitle": self.get_report_subtitle(report_data),
            "form": form,
            "report_data": report_data,
            "filter_blocks": self.get_filter_blocks(),
            "filter_actions": self.get_filter_actions(),
            "summary_cards": self.get_summary_cards(report_data),
            "screen_columns": self.get_screen_columns(),
            "print_columns": self.get_print_columns(),
            "export_columns": self.get_export_columns(),
            "table_rows": self.get_table_rows(report_data),
            "screen_grid_columns": self.get_screen_grid_columns(report_data),
            "screen_grid_rows": self.get_screen_grid_rows(report_data),
            "export_query": export_query,
            "report_actions": self.get_report_actions(),
            "report_table_id": self.report_table_id,
            "print_settings": self.get_print_settings(),
        }

    def is_ajax_request(self):
        return self.request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def build_ajax_payload(self, *, form, report_data):
        context = self.get_report_context(
            form=form,
            report_data=report_data,
            export_query=self.get_export_query() if report_data else "",
        )
        return {
            "success": form.is_valid(),
            "form_html": render_to_string(
                "components/report/report_filters_panel.html",
                context,
                request=self.request,
            ),
            "results_html": render_to_string(
                "components/report/report_results.html",
                context,
                request=self.request,
            ),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        report_data = self.build_report_data(form.cleaned_data) if self.should_generate(form) else None
        context.update(
            self.get_report_context(
                form=form,
                report_data=report_data,
                export_query=self.get_export_query() if report_data else "",
            )
        )
        return context

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        export_format = self.get_export_format()
        if export_format and form.is_valid():
            report_data = self.build_report_data(form.cleaned_data)
            response = self.build_export_response(report_data, export_format)
            if response is not None:
                return response
        if self.is_ajax_request():
            report_data = self.build_report_data(form.cleaned_data) if self.should_generate(form) else None
            return JsonResponse(self.build_ajax_payload(form=form, report_data=report_data))
        return super().get(request, *args, **kwargs)

from __future__ import annotations

from typing import Any, Dict, Optional

from django.template import Context, Template

from nepanest.modules.payroll.models import ReportTemplate


def _merge_html(*parts: str) -> str:
    return "\n".join(part.strip() for part in parts if (part or "").strip())


def resolve_report_template(
    *,
    report_key: str,
    organization_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    template_code: Optional[str] = None,
) -> Optional[ReportTemplate]:
    queryset = ReportTemplate.objects.select_related("layout").filter(is_active=True)
    if template_code:
        return queryset.filter(code=template_code).first()

    if branch_id:
        template = queryset.filter(
            report_key=report_key,
            branch_id=branch_id,
            is_default=True,
        ).first()
        if template:
            return template

    if organization_id:
        template = queryset.filter(
            report_key=report_key,
            organization_id=organization_id,
            branch__isnull=True,
            is_default=True,
        ).first()
        if template:
            return template

    template = queryset.filter(
        report_key=report_key,
        organization__isnull=True,
        branch__isnull=True,
        is_default=True,
    ).first()
    if template:
        return template

    return queryset.filter(
        report_key=report_key,
        organization__isnull=True,
        branch__isnull=True,
    ).first()


def render_report_html(
    *,
    report_key: str,
    context_data: Optional[Dict[str, Any]] = None,
    organization_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    template_code: Optional[str] = None,
) -> str:
    template = resolve_report_template(
        report_key=report_key,
        organization_id=organization_id,
        branch_id=branch_id,
        template_code=template_code,
    )
    if not template:
        return ""

    data = dict(template.sample_context or {})
    data.update(context_data or {})

    rendered_body = Template(template.body_html).render(Context(data))
    rendered_header = Template(template.header_html or template.layout.header_html or "").render(
        Context(data)
    )
    rendered_footer = Template(template.footer_html or template.layout.footer_html or "").render(
        Context(data)
    )

    wrapper_context = Context(
        {
            **data,
            "report_body": rendered_body,
            "report_header": rendered_header,
            "report_footer": rendered_footer,
            "report_styles": _merge_html(template.layout.css_content, template.css_content),
        }
    )
    return Template(template.layout.html_wrapper).render(wrapper_context)

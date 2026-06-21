from django.utils.html import format_html
from django.urls import reverse
from core.utils.urls import reverse_with_request


class DataTableActionButtons:
    """
    Reusable DataTable Action Button Builder
    """

    def __init__(self, buttons: list, request=None):
        self.buttons = buttons
        self.request = request

    def build_attributes(self, attributes: dict, object_id):
        """
        Convert attribute dict to HTML attributes string
        """
        attr_html = ""

        for key, value in attributes.items():
            if isinstance(value, str):
                value = value.format(id=object_id)
            attr_html += f' {key}="{value}"'

        return attr_html

    def render(self, obj):
        html = ""

        for btn in self.buttons:

            # 🔐 Permission check (optional)
            permission = btn.get("permission")
            if permission and self.request:
                if not self.request.user.has_perm(permission):
                    continue

            # 🔗 URL handling (supports reverse name or raw url)
            if btn.get("reverse"):
                # prefer request namespace when available
                url = reverse_with_request(btn["reverse"], request=self.request, args=[obj.id])
            else:
                url = btn.get("url", "#").format(id=obj.id)

            label = btn.get("label", "")
            css_class = btn.get("class", "btn btn-sm btn-secondary")
            icon = btn.get("icon", "")
            attributes = btn.get("attributes", {})

            # Optional confirm dialog
            confirm = btn.get("confirm")
            if confirm:
                attributes["onclick"] = f"return confirm('{confirm}')"

            attr_html = self.build_attributes(attributes, obj.id)

            button_html = f"""
                <a href="{url}" class="{css_class}" {attr_html}>
                    <i class="{icon}"></i> {label}
                </a>
            """

            html += button_html

        return format_html(html)
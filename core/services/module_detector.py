
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ModuleInfo:
    """
    Immutable ERP context result returned by ModuleDetectorService.detect().

    Attributes:
        module_name:      First URL segment e.g. "registry", "crm", "payroll"
        display_name:     Human-friendly ERP area name
        icon:             Feather icon name to represent the area
        domains:          Functional domains covered by the area
        layout_template:  Template path to extend for this area
        is_known:         False if module_name is not in the registry map
        metadata:         Extra metadata for future ERP expansion
    """
    module_name: str
    display_name: str
    icon: str
    domains: tuple[str, ...]
    layout_template: str
    is_known: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class ModuleDetectorService:
    ERP_AREA_MAP: dict[str, dict[str, Any]] = {
        # platform
        "registry": {
            "display_name": "Registry",
            "icon": "database",
            "domains": ("platform", "registry"),
            "layout_template": "registry/layouts/base.html",
            "kind": "platform",
        },
        # foundation
        "organization": {
            "display_name": "Organization",
            "icon": "building",
            "domains": ("foundation", "organization"),
            "layout_template": "organization/layouts/base.html",
            "kind": "foundation",
        },
        "geography": {
            "display_name": "Geography",
            "icon": "map",
            "domains": ("foundation", "location"),
            "layout_template": "geography/layouts/base.html",
            "kind": "foundation",
        },
        # reusable modules
        "accounting": {
            "display_name": "Accounting",
            "icon": "book-open",
            "domains": ("finance", "accounting"),
            "layout_template": "accounting/layouts/base.html",
            "kind": "module",
        },
        "finance": {
            "display_name": "Finance",
            "icon": "percent",
            "domains": ("finance",),
            "layout_template": "finance/layouts/base.html",
            "kind": "module",
        },
        "billing": {
            "display_name": "Billing",
            "icon": "receipt",
            "domains": ("finance", "billing"),
            "layout_template": "billing/layouts/base.html",
            "kind": "module",
        },
        "assets": {
            "display_name": "Assets",
            "icon": "briefcase",
            "domains": ("operations", "asset-management"),
            "layout_template": "assets/layouts/base.html",
            "kind": "module",
        },
        "hrm": {
            "display_name": "Human Resources",
            "icon": "users",
            "domains": ("people", "human-resources"),
            "layout_template": "hrm/layouts/base.html",
            "kind": "module",
        },
        "payroll": {
            "display_name": "Payroll",
            "icon": "wallet",
            "domains": ("people", "compensation"),
            "layout_template": "payroll/layouts/base.html",
            "kind": "module",
        },
        "recruitment": {
            "display_name": "Recruitment",
            "icon": "user-plus",
            "domains": ("people", "talent-acquisition"),
            "layout_template": "recruitment/layouts/base.html",
            "kind": "module",
        },
        "leave": {
            "display_name": "Leave",
            "icon": "calendar",
            "domains": ("people", "attendance"),
            "layout_template": "leave/layouts/base.html",
            "kind": "module",
        },
        "attendance": {
            "display_name": "Attendance",
            "icon": "clock",
            "domains": ("people", "attendance"),
            "layout_template": "attendance/layouts/base.html",
            "kind": "module",
        },
        "projects": {
            "display_name": "Projects",
            "icon": "folder-kanban",
            "domains": ("operations", "project-management"),
            "layout_template": "projects/layouts/base.html",
            "kind": "module",
        },
        "tasks": {
            "display_name": "Tasks",
            "icon": "check-square",
            "domains": ("operations", "task-management"),
            "layout_template": "tasks/layouts/base.html",
            "kind": "module",
        },
        # products
        "gym": {
            "display_name": "HamroGym",
            "icon": "activity",
            "domains": ("fitness", "membership"),
            "layout_template": "hamrogym/layouts/base.html",
            "kind": "product",
        },
        "crm": {
            "display_name": "CRM",
            "icon": "briefcase",
            "domains": ("sales", "customer-relationships"),
            "layout_template": "crm/layouts/base.html",
            "kind": "module",
        },
    }

    DEFAULT_LAYOUT = "layouts/base.html"

    def detect(self, path: str) -> ModuleInfo:
        """
        Detect an ERP area from a URL path string.

        Args:
            path: Request path e.g. "/registry/clients/1/"

        Returns:
            ModuleInfo dataclass with module_name, display_name, icon, domains, layout_template, is_known
        """
        module_name = self._extract_first_segment(path)
        area_config = self.ERP_AREA_MAP.get(module_name)

        if area_config:
            return ModuleInfo(
                module_name=module_name,
                display_name=area_config["display_name"],
                icon=area_config["icon"],
                domains=tuple(area_config.get("domains", ())),
                layout_template=area_config["layout_template"],
                is_known=True,
                metadata={key: value for key, value in area_config.items() if key not in {"display_name", "icon", "domains", "layout_template"}},
            )

        return ModuleInfo(
            module_name=module_name or "unknown",
            display_name=self._format_display_name(module_name),
            icon="circle",
            domains=(),
            layout_template=self.DEFAULT_LAYOUT,
            is_known=False,
            metadata={},
        )

    def is_known_module(self, path: str) -> bool:
        """Quick check - is this path under a known ERP area?"""
        return self.detect(path).is_known

    def get_layout(self, path: str) -> str:
        """Shortcut — just return the layout template string."""
        return self.detect(path).layout_template

    def _extract_first_segment(self, path: str) -> str:
        """
        Extract first non-empty path segment.

        "/registry/clients/1/"  →  "registry"
        "/crm/"                 →  "crm"
        "/"                     →  ""
        """
        path = path.lstrip("/")
        return path.split("/")[0] if path else ""

    def _format_display_name(self, module_name: str) -> str:
        if not module_name:
            return "ERP"
        return module_name.replace("-", " ").replace("_", " ").title()

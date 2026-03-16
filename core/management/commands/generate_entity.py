from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Generate CRUD scaffolding (entity config, datatable, form) for an app."

    def add_arguments(self, parser):
        parser.add_argument("app_label", help="Django app label, e.g. core or payrollhr")
        parser.add_argument("entity_name", help="Entity name in snake_case, e.g. fiscal_year")
        parser.add_argument("model_name", help="Model class name, e.g. FiscalYear")
        parser.add_argument("--group", default="", help="Entities subpackage (single segment), e.g. master")
        parser.add_argument("--url-path", default="", help="URL path segment, e.g. fiscal-years")
        parser.add_argument("--verbose-name", default="", help="Verbose name for UI")
        parser.add_argument(
            "--create-model",
            action="store_true",
            help="Also scaffold a model in app models (models/<entity>.py or models.py)",
        )
        parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    def handle(self, *args, **options):
        app_label = options["app_label"]
        entity_name = options["entity_name"].strip()
        model_name = options["model_name"].strip()
        group = options["group"].strip()
        url_path = options["url_path"].strip()
        verbose_name = options["verbose_name"].strip()
        create_model = options["create_model"]
        force = options["force"]

        if not entity_name or not model_name:
            raise CommandError("entity_name and model_name are required")

        if "/" in group or "\\" in group:
            raise CommandError("group must be a single segment (e.g., master)")

        try:
            app_config = apps.get_app_config(app_label)
        except LookupError as exc:
            raise CommandError(f"Unknown app label: {app_label}") from exc

        base_path = Path(app_config.path)

        if not url_path:
            url_base = entity_name.replace("_", "-")
            url_path = url_base if url_base.endswith("s") else f"{url_base}s"

        if not verbose_name:
            verbose_name = entity_name.replace("_", " ").title()

        entities_root = base_path / "entities"
        entities_root.mkdir(parents=True, exist_ok=True)
        self._ensure_init(entities_root)

        entity_dir = entities_root
        if group:
            entity_dir = entities_root / group
            entity_dir.mkdir(parents=True, exist_ok=True)
            self._ensure_init(entity_dir)
            self._ensure_import(entities_root / "__init__.py", f"from . import {group}  # noqa: F401")
            self._ensure_import(entity_dir / "__init__.py", f"from . import {entity_name}  # noqa: F401")
        else:
            self._ensure_import(entities_root / "__init__.py", f"from . import {entity_name}  # noqa: F401")

        datatables_dir = base_path / "datatables"
        datatables_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_init(datatables_dir)

        forms_dir = base_path / "forms"
        forms_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_init(forms_dir)

        entity_file = entity_dir / f"{entity_name}.py"
        datatable_file = datatables_dir / f"{entity_name}_data_table.py"
        form_file = forms_dir / f"{entity_name}_form.py"

        if not force:
            for path in (entity_file, datatable_file, form_file):
                if path.exists():
                    raise CommandError(f"File already exists: {path}")

        rel_prefix = "..." if group else ".."
        model_class_name = self._normalize_model_name(model_name)
        datatable_class = f"{model_class_name}DataTableView"
        form_class = f"{model_class_name}Form"

        model_output = None
        if create_model:
            model_output = self._ensure_model(
                base_path=base_path,
                model_name=model_class_name,
                entity_name=entity_name,
                force=force,
            )

        entity_content = f"""from core.config import EntityConfig\nfrom core.registry import register_entity\nfrom {rel_prefix}datatables.{entity_name}_data_table import {datatable_class}, {entity_name.upper()}_COLUMNS\nfrom {rel_prefix}forms.{entity_name}_form import {form_class}\nfrom {rel_prefix}models import {model_class_name}\n\n\nregister_entity(\n    EntityConfig(\n        name=\"{entity_name}\",\n        url_path=\"{url_path}\",\n        verbose_name=\"{verbose_name}\",\n        model={model_class_name},\n        form_class={form_class},\n        datatable_view={datatable_class},\n        fields=[\n            # TODO: define fields\n            # {{\"name\": \"name\", \"label\": \"Name\", \"type\": \"text\", \"required\": True, \"col\": 6}},\n        ],\n        datatable_columns=[\n            {{\"name\": key, \"title\": key.replace(\"_\", \" \").title()}}\n            for key, _accessor in {entity_name.upper()}_COLUMNS\n            if key != \"id\"\n        ],\n        reset_defaults={{}},\n    )\n)\n"""

        datatable_content = f"""from core.datatables.views import BaseDataTableView\nfrom ..models import {model_class_name}\n\n\n{entity_name.upper()}_COLUMNS = [\n    (\"id\", \"id\"),\n    # TODO: add columns\n]\n\n\nclass {datatable_class}(BaseDataTableView):\n    model = {model_class_name}\n    columns = {entity_name.upper()}_COLUMNS\n    searchable_columns = [\n        # TODO: add searchable fields\n    ]\n    orderable_columns = [\n        # TODO: add orderable fields\n    ]\n"""

        form_content = f"""from django import forms\n\nfrom ..models import {model_class_name}\n\n\nclass {form_class}(forms.ModelForm):\n    class Meta:\n        model = {model_class_name}\n        fields = [\n            # TODO: add fields\n        ]\n"""

        entity_file.write_text(entity_content)
        datatable_file.write_text(datatable_content)
        form_file.write_text(form_content)

        self.stdout.write(self.style.SUCCESS("Generated entity scaffolding:"))
        self.stdout.write(f"- {entity_file}")
        self.stdout.write(f"- {datatable_file}")
        self.stdout.write(f"- {form_file}")
        if model_output:
            self.stdout.write(f"- {model_output}")

    def _ensure_init(self, directory: Path) -> None:
        init_file = directory / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")

    def _ensure_import(self, init_file: Path, line: str) -> None:
        content = ""
        if init_file.exists():
            content = init_file.read_text()
        if line in content:
            return
        content = content.rstrip()
        if content:
            content += "\n"
        content += line + "\n"
        init_file.write_text(content)

    def _ensure_model(
        self, *, base_path: Path, model_name: str, entity_name: str, force: bool
    ) -> str:
        models_dir = base_path / "models"
        models_py = base_path / "models.py"

        if models_dir.exists():
            models_dir.mkdir(parents=True, exist_ok=True)
            self._ensure_init(models_dir)
            model_file = models_dir / f"{entity_name}.py"
            if model_file.exists() and not force:
                raise CommandError(f"Model file already exists: {model_file}")
            model_content = self._model_template(model_name)
            model_file.write_text(model_content)
            self._ensure_import(models_dir / "__init__.py", f"from .{entity_name} import {model_name}")
            return str(model_file)

        if models_py.exists():
            content = models_py.read_text()
            if f"class {model_name}(" in content and not force:
                raise CommandError(f"Model class already exists in: {models_py}")
            if content and not content.endswith("\n"):
                content += "\n"
            content += "\n" + self._model_template(model_name)
            models_py.write_text(content)
            return str(models_py)

        # Default to models.py if models/ doesn't exist yet.
        model_content = self._model_template(model_name)
        models_py.write_text(model_content)
        return str(models_py)

    # def _model_template(self, model_name: str) -> str:
    #     return (
    #         "from django.db import models\n\n\n"
    #         f"class {model_name}(models.Model):\n"
    #         "    name = models.CharField(max_length=100, unique=True)\n"
    #         "    is_active = models.BooleanField(default=True)\n"
    #         "    remarks = models.TextField(blank=True)\n"
    #         "    created_at = models.DateTimeField(auto_now_add=True)\n"
    #         "    updated_at = models.DateTimeField(auto_now=True)\n\n"
    #         "    class Meta:\n"
    #         "        ordering = [\"name\"]\n\n"
    #         "    def __str__(self) -> str:\n"
    #         "        return self.name\n"
    #     )

    def _model_template(self, class_name: str) -> str:
        return (
            "from django.db import models\n\n\n"
            f"class {class_name}(models.Model):\n"
            "    name = models.CharField(max_length=100, unique=True)\n"
            "    is_active = models.BooleanField(default=True)\n"
            "    remarks = models.TextField(blank=True)\n"
            "    created_at = models.DateTimeField(auto_now_add=True)\n"
            "    updated_at = models.DateTimeField(auto_now=True)\n\n"
            "    class Meta:\n"
            "        ordering = [\"name\"]\n\n"
            "    def __str__(self) -> str:\n"
            "        return self.name\n"
        )

    def _normalize_model_name(self, model_name: str) -> str:
        if "_" in model_name or model_name.islower():
            return "".join(word.capitalize() for word in model_name.split("_") if word)
        return model_name

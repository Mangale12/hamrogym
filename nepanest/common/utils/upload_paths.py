from datetime import datetime

from django.utils.text import slugify


def build_upload_path(
    *,
    base_dir: str,
    instance,
    filename: str,
    field_name: str,
    name_attr: str = "name",
    tenant_code: str | None = None,
) -> str:
    raw_name = getattr(instance, name_attr, None) or "record"
    safe_name = slugify(raw_name) or "record"
    original_name = slugify(filename.rsplit(".", 1)[0] or "file") or "file"
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_name = f"{safe_name}_{original_name}_{timestamp}"
    if ext:
        final_name = f"{final_name}.{ext}"

    parts = [base_dir]
    if tenant_code:
        parts.append(slugify(tenant_code) or "tenant")
    parts.extend([safe_name, field_name, final_name])
    return "/".join(parts)

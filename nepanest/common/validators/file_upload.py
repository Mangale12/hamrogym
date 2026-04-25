from pathlib import Path

from django.core.exceptions import ValidationError


def validate_file_extension(value, *, allowed_extensions):
    extension = Path(value.name).suffix.lower().lstrip(".")
    normalized_extensions = {ext.lower().lstrip(".") for ext in allowed_extensions}

    if extension not in normalized_extensions:
        allowed_list = ", ".join(sorted(normalized_extensions))
        raise ValidationError(
            f"Unsupported file type. Allowed file types are: {allowed_list}."
        )


def validate_file_size(value, *, max_size_mb):
    max_size_bytes = max_size_mb * 1024 * 1024
    if value.size > max_size_bytes:
        raise ValidationError(f"File size must not exceed {max_size_mb} MB.")

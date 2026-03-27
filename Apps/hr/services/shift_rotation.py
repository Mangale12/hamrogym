from django.db import models
from django.utils import timezone

from Apps.hr.models import Employee, EmployeeShift, Shift

def _rotation_queryset(employee: Employee, at_time=None):
    at_time = at_time or timezone.localtime()
    return (
        EmployeeShift.objects.filter(employee=employee)
        .filter(models.Q(effective_from__isnull=True) | models.Q(effective_from__lte=at_time))
        .filter(models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=at_time))
        .select_related("shift")
        .order_by("-effective_from", "-created_at", "-id")
    )


def resolve_employee_shift(employee: Employee, at_time=None):
    if employee is None:
        return None

    at_time = at_time or timezone.localtime()
    cache_key = "_current_shift_rotation"
    cached_rotation = getattr(employee, cache_key, None)
    if cached_rotation is not None:
        return cached_rotation.shift if cached_rotation else _resolve_legacy_shift(employee)

    rotation = _rotation_queryset(employee, at_time=at_time).first()
    setattr(employee, cache_key, rotation)
    if rotation:
        return rotation.shift
    return _resolve_legacy_shift(employee)


def current_shift_rotation(employee: Employee, at_time=None):
    if employee is None:
        return None

    at_time = at_time or timezone.localtime()
    cache_key = "_current_shift_rotation"
    cached_rotation = getattr(employee, cache_key, None)
    if cached_rotation is not None:
        return cached_rotation

    rotation = _rotation_queryset(employee, at_time=at_time).first()
    setattr(employee, cache_key, rotation)
    return rotation


def _resolve_legacy_shift(employee: Employee):
    shift_value = (employee.shift or "").strip()
    if not shift_value:
        return None
    return (
        Shift.objects.filter(code__iexact=shift_value).first()
        or Shift.objects.filter(name__iexact=shift_value).first()
    )

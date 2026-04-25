from django.db.models import Q

from core.datatables.views import BaseDataTableView
from ..models import BillingProfile


BILLING_PROFILE_COLUMNS = [
    ("id", "id"),
    ("name", "name"),
    ("billing_type", lambda obj: obj.get_billing_type_display()),
    ("related_object", lambda obj: obj.related_object_label),
    ("currency", lambda obj: getattr(obj.currency, "code", "")),
    ("tax_number", "tax_number"),
    ("registration_number", "registration_number"),
    ("credit_limit", "credit_limit"),
    ("is_active", lambda obj: "Yes" if obj.is_active else "No"),
    ("remarks", "remarks"),
]


class BillingProfileDataTableView(BaseDataTableView):
    model = BillingProfile
    columns = BILLING_PROFILE_COLUMNS
    searchable_columns = [
        "name",
        "billing_type",
        "currency__code",
        "currency__name",
        "tax_number",
        "registration_number",
        "remarks",
    ]
    orderable_columns = [
        "name",
        "billing_type",
        "content_type__model",
        "currency__code",
        "tax_number",
        "registration_number",
        "credit_limit",
        "is_active",
        "remarks",
    ]

    def get_queryset(self):
        return super().get_queryset().select_related("currency", "content_type")

    def filter_queryset(self, queryset, search_value):
        if not search_value:
            return queryset

        base_queryset = queryset
        queryset = super().filter_queryset(base_queryset, search_value)
        app_registry = self.model._meta.apps
        organization_model = app_registry.get_model("core", "Organization")
        vendor_model = app_registry.get_model("assets", "AssetVendor")
        department_model = app_registry.get_model("hr", "Department")

        # Build object id lookups for supported generic relations so the linked entity name
        # can be searched from the billing profile list.
        organization_ids = list(
            organization_model.objects.filter(name__icontains=search_value).values_list("pk", flat=True)
        )
        vendor_ids = list(
            vendor_model.objects.filter(name__icontains=search_value).values_list("pk", flat=True)
        )
        department_ids = list(
            department_model.objects.filter(name__icontains=search_value).values_list("pk", flat=True)
        )

        related_queries = (
            Q(content_type__app_label="core", content_type__model="organization", object_id__in=organization_ids)
            | Q(content_type__app_label="assets", content_type__model="assetvendor", object_id__in=vendor_ids)
            | Q(content_type__app_label="hr", content_type__model="department", object_id__in=department_ids)
        )

        return (queryset | base_queryset.filter(related_queries)).distinct()

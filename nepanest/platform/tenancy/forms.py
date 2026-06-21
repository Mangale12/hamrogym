from django import forms
from django.core.exceptions import ValidationError

from core.forms import RememberMeAuthenticationForm

from .context import (
    TenantLookupError,
    get_current_database_alias,
    resolve_tenant_by_code,
    set_current_tenant,
)


class TenantAwareAuthenticationForm(RememberMeAuthenticationForm):
    tenant_code = forms.CharField(
        label="Code",
        max_length=30,
        help_text="Enter the tenant or workspace code before your username.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tenant_code"].widget.attrs.update(
            {
                "placeholder": "Enter workspace code",
                "autocomplete": "off",
            }
        )

    def clean(self):
        tenant_code = self.cleaned_data.get("tenant_code")
        try:
            tenant = resolve_tenant_by_code(tenant_code)
        except TenantLookupError as exc:
            raise ValidationError({"tenant_code": str(exc)})

        if tenant is None:
            raise ValidationError({"tenant_code": "Invalid or inactive workspace code."})

        set_current_tenant(tenant)
        if self.request is not None:
            self.request.tenant = tenant
            self.request.tenant_code = tenant.code
            self.request.tenant_database_alias = get_current_database_alias()

        return super().clean()

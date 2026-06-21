from core.views.auth import RememberMeLoginView

from .forms import TenantAwareAuthenticationForm


class TenantLoginView(RememberMeLoginView):
    authentication_form = TenantAwareAuthenticationForm

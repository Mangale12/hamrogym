from django.conf import settings
from django.contrib.auth.views import LoginView

from core.forms import RememberMeAuthenticationForm


class RememberMeLoginView(LoginView):
    authentication_form = RememberMeAuthenticationForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        remember_me = form.cleaned_data.get("remember_me")

        if remember_me:
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(0)

        return response

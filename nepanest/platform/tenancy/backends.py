from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class TenantModelBackend(ModelBackend):
    """
    Authenticates against the tenant database.
    The DB is already set in thread-local by LoginView
    before authenticate() is called, so this backend
    just works like the default — no extra code needed.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)  # timing attack prevention
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
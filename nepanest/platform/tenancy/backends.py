from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import connections

from .context import get_current_database_alias

UserModel = get_user_model()


class TenantModelBackend(ModelBackend):
    """
    Authenticates against the tenant database selected for the current request.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        database = get_current_database_alias()
        db_settings = connections[database].settings_dict
        print(
            "[tenant-login] authenticating "
            f"username={username} alias={database} "
            f"db_name={db_settings.get('NAME')} db_user={db_settings.get('USER')} "
            f"db_host={db_settings.get('HOST')} db_port={db_settings.get('PORT')}"
        )
        try:
            user = UserModel._default_manager.db_manager(database).get_by_natural_key(username)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)  # timing attack prevention
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

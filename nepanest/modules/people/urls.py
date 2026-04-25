from django.urls import path


def user_select(request, *args, **kwargs):
    from nepanest.modules.human_resources.views.user_select import user_select as legacy_user_select

    return legacy_user_select(request, *args, **kwargs)


app_name = "people"

urlpatterns = [
    path("select/users/", user_select, name="user_select"),
]

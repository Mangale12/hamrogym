from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("config.auth_urls")),
    path("", RedirectView.as_view(pattern_name="crm_dashboard", permanent=False)),
    path("crm/", include("nepanest.modules.crm.urls")),
    path("core/crm/", include(("nepanest.modules.crm.urls", "crm"), namespace="crm_core")),
    path("hr/", include("nepanest.modules.human_resources.urls")),
    path("core/", include("nepanest.modules.assets.urls")),
    path("core/", include("nepanest.modules.accounting.urls")),
    path("core/", include("nepanest.modules.finance.urls")),
    path("core/", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from core.views import site_data, serve_site

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/site-data/", site_data),
    path("", serve_site, {"path": "index.html"}),
    re_path(r"^(?P<path>styles\.css|script\.js)$", serve_site),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.contrib import admin
from django.urls import path, re_path
from core.views import robots_txt, site_data, serve_site

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/site-data/", site_data),
    path("robots.txt", robots_txt),
    path("", serve_site, {"path": "index.html"}),
    re_path(r"^(?P<path>styles\.css|script\.js)$", serve_site),
]

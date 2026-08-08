from core.views import robots_txt, serve_asset, serve_site, site_data
from django.contrib import admin
from django.urls import path, re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/site-data/", site_data),
    path("robots.txt", robots_txt),
    path("projects/", serve_site, {"path": "index.html"}),
    path("projects/<slug:slug>/", serve_site, {"path": "index.html"}),
    path("work/", serve_site, {"path": "index.html"}),
    re_path(r"^assets/(?P<path>.+)$", serve_asset),
    path("", serve_site, {"path": "index.html"}),
    re_path(r"^(?P<path>styles\.css|script\.js)$", serve_site),
]

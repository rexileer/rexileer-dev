from core.views import (
    robots_txt,
    serve_asset,
    serve_site,
    site_data,
    site_event,
    sitemap,
)
from django.contrib import admin
from django.urls import path, re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/site-data/", site_data),
    path("api/events/", site_event),
    path("sitemap.xml", sitemap),
    path("robots.txt", robots_txt),
    path("projects/", serve_site, {"path": "index.html"}),
    path("projects/<slug:slug>/", serve_site, {"path": "index.html"}),
    path("work/", serve_site, {"path": "index.html"}),
    path("services/", serve_site),
    path("services/<slug:slug>/", serve_site),
    path("en/", serve_site, {"lang": "en"}),
    path("en/services/", serve_site, {"lang": "en"}),
    path("en/services/<slug:slug>/", serve_site, {"lang": "en"}),
    path("en/projects/", serve_site, {"lang": "en"}),
    path("en/projects/<slug:slug>/", serve_site, {"lang": "en"}),
    path("en/work/", serve_site, {"lang": "en"}),
    re_path(r"^assets/(?P<path>.+)$", serve_asset),
    path("", serve_site, {"path": "index.html"}),
    re_path(r"^(?P<path>styles\.css|script\.js)$", serve_site),
]

handler404 = "core.views.not_found"

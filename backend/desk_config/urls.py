from desk import document_views, views
from django.urls import path

urlpatterns = [
    path("", views.today),
    path("login/", views.sign_in),
    path("logout/", views.sign_out),
    path("password/", views.password),
    path("calendar/", views.calendar),
    path("records/<str:entity>/", views.records),
    path("records/<str:entity>/new/", views.edit),
    path("records/<str:entity>/<int:pk>/", views.edit),
    path("data/", views.data_tools),
    path("data/export/", views.export),
    path("history/", views.history),
    path("assets/<path:name>", views.asset),
    path("health/", views.health),
    path("robots.txt", views.robots),
    path("documents/", document_views.documents),
    path("documents/new/", document_views.document),
    path("documents/<int:pk>/", document_views.document),
    path(
        "documents/<int:pk>/download/",
        document_views.document_bytes,
        {"mode": "download"},
    ),
    path(
        "documents/<int:pk>/preview/",
        document_views.document_bytes,
        {"mode": "preview"},
    ),
]

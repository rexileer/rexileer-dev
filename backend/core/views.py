import os
from pathlib import Path
from django.http import Http404, HttpResponse, JsonResponse

# В контейнере: /app/site. Локально: репо с backend/ и site/ — родитель репо / site
_SITE_DIR = os.environ.get("SITE_DIR")
if _SITE_DIR:
    SITE_DIR = Path(_SITE_DIR)
else:
    _root = Path(__file__).resolve().parent.parent.parent
    SITE_DIR = _root / "site"
ALLOWED_SITE_FILES = {"index.html", "styles.css", "script.js"}


def serve_site(request, path="index.html"):
    if path not in ALLOWED_SITE_FILES:
        raise Http404
    file_path = SITE_DIR / path
    if not file_path.is_file():
        raise Http404
    content_type = "text/html" if path.endswith(".html") else "text/css" if path.endswith(".css") else "application/javascript"
    return HttpResponse(file_path.read_bytes(), content_type=content_type)


def site_data(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)
    from .serializers import build_site_data
    return JsonResponse(build_site_data())

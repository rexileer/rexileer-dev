from pathlib import Path
from django.http import Http404, HttpResponse, JsonResponse

SITE_DIR = Path(__file__).resolve().parent.parent.parent / "site"
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

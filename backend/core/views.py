import hashlib
import mimetypes
import os
from pathlib import Path

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .content import SERVICES
from .models import Project, SiteEvent
from .presentation import (
    BASE_URL,
    page_context,
    published_projects,
    structured_data,
)

# В контейнере: /app/site. Локально: репо с backend/ и site/ — родитель репо / site
_SITE_DIR = os.environ.get("SITE_DIR")
if _SITE_DIR:
    SITE_DIR = Path(_SITE_DIR)
else:
    _root = Path(__file__).resolve().parent.parent.parent
    SITE_DIR = _root / "site"
ALLOWED_SITE_FILES = {"index.html", "styles.css", "script.js"}


@ensure_csrf_cookie
def serve_site(request, path="index.html", lang="ru", **_route_params):
    if path == "index.html":
        return serve_page(request, lang)
    if path not in ALLOWED_SITE_FILES:
        raise Http404
    file_path = SITE_DIR / path
    if not file_path.is_file():
        raise Http404
    content_type = (
        "text/html"
        if path.endswith(".html")
        else "text/css"
        if path.endswith(".css")
        else "application/javascript"
    )
    return HttpResponse(file_path.read_bytes(), content_type=content_type)


def serve_page(request, lang):
    context = page_context(request, lang)
    projects = published_projects(lang)
    base_path = request.path[3:] if request.path.startswith("/en/") else request.path
    path = base_path.rstrip("/") or "/"
    ui = context["ui"]
    context["title"] = ui["home_seo"]
    context["description"] = ui["hero_lead"]
    context["projects"] = projects
    context["asset_version"] = hashlib.sha256(
        (SITE_DIR / "styles.css").read_bytes()
        + (SITE_DIR / "script.js").read_bytes()
        + (SITE_DIR / "assets" / "fonts" / "fonts.css").read_bytes()
    ).hexdigest()[:12]
    template = "home"
    kind = "WebPage"
    extra = None
    if path == "/":
        selected = [
            "ai-lead-scoring",
            "ai-consultant-bitrix-rag",
            "meatbot-production-crm",
            "avito-parts-parser",
            "priceflow-ai",
            "payment-broadcast-bot",
        ]
        context["selected"] = [
            p for slug in selected for p in projects if p["id"] == slug
        ]
    elif path == "/services":
        template = "services"
        context["title"] = ui["services_seo"]
        context["description"] = ui["services_lead"]
        kind = "CollectionPage"
    elif path.startswith("/services/"):
        service = next(
            (s for s in context["services"] if s["slug"] == path.split("/")[-1]), None
        )
        if service is None:
            raise Http404
        template = "service"
        context["service"] = service
        context["related_services"] = [
            s for s in context["services"] if s["slug"] != service["slug"]
        ]
        context["selected"] = [
            p for slug in service["projects"] for p in projects if p["id"] == slug
        ]
        context["title"] = service["seo"]
        context["description"] = service["lead"]
        extra = {
            "about": {
                "@type": "Service",
                "name": service["title"],
                "serviceType": service["title"],
                "provider": {"@type": "Person", "name": "Rexileer", "url": BASE_URL},
            },
            "mainEntity": {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": item["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
                    }
                    for item in service["faq"]
                ],
            },
        }
    elif path in ("/projects", "/work"):
        template = "catalog"
        context["is_work"] = path == "/work"
        context["selected"] = [
            p for p in projects if p["featured"] != context["is_work"]
        ]
        context["title"] = (
            ui["work_title"] if context["is_work"] else ui["cases_title"]
        ) + " — Rexileer"
        context["description"] = (
            ui["work_lead"] if context["is_work"] else ui["cases_lead"]
        )
        kind = "CollectionPage"
    elif path.startswith("/projects/"):
        project = next((p for p in projects if p["id"] == path.split("/")[-1]), None)
        if project is None:
            raise Http404
        template = "project"
        context["project"] = project
        context["contact_title"] = ui["similar"]
        context["contact_lead"] = ui["case_inquiry"]
        context["title"] = project["title"] + " — Rexileer"
        context["description"] = project["description"]
        index = projects.index(project)
        context["next_project"] = projects[(index + 1) % len(projects)]
        context["related_services"] = project["services"]
        if project["cover"].get("url", "").startswith("/assets/projects/"):
            context["og_image"] = BASE_URL + project["cover"]["url"]
        kind = "CreativeWork"
    else:
        raise Http404
    context["schema"] = structured_data(context, kind, extra)
    response = render(request, f"core/site/{template}.html", context)
    response["Content-Language"] = lang
    response["Cache-Control"] = "no-cache"
    return response


@require_POST
def site_event(request):
    try:
        content_length = int(request.META.get("CONTENT_LENGTH") or 0)
    except ValueError:
        return JsonResponse({"error": "invalid payload length"}, status=400)
    if content_length > 2048:
        return JsonResponse({"error": "payload too large"}, status=400)
    name = request.POST.get("name")
    location = request.POST.get("location")
    path = request.POST.get("path", "")
    lang = request.POST.get("lang")
    if (
        name not in {"telegram_click", "email_click", "case_open"}
        or location
        not in {
            "header",
            "hero",
            "rescue",
            "cases",
            "contact",
            "service",
            "project",
            "footer",
        }
        or lang not in {"ru", "en"}
        or not path.startswith("/")
        or len(path) > 255
        or any(char in path for char in "?\r\n")
    ):
        return JsonResponse({"error": "invalid event"}, status=400)
    SiteEvent.objects.create(name=name, location=location, path=path, lang=lang)
    return HttpResponse(status=204)


def sitemap(request):
    from xml.sax.saxutils import escape

    paths = ["/", "/services/", "/projects/", "/work/"]
    paths += [f"/services/{s['slug']}/" for s in SERVICES]
    paths += [
        f"/projects/{slug}/"
        for slug in Project.objects.filter(status=Project.Status.PUBLISHED).values_list(
            "slug", flat=True
        )
    ]
    urls = [BASE_URL + prefix + path for path in paths for prefix in ("", "/en")]
    content = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    content += "".join(f"<url><loc>{escape(url)}</loc></url>" for url in urls)
    content += "</urlset>"
    return HttpResponse(content, content_type="application/xml")


def not_found(request, exception):
    lang = "en" if request.path.startswith("/en/") else "ru"
    context = page_context(request, lang)
    context.update(
        title=context["ui"]["not_found"] + " — Rexileer",
        description="",
        noindex=True,
        asset_version="1",
    )
    return render(request, "core/site/404.html", context, status=404)


def serve_asset(request, path):
    asset_root = (SITE_DIR / "assets").resolve()
    file_path = (asset_root / path).resolve()
    try:
        file_path.relative_to(asset_root)
    except ValueError as exc:
        raise Http404 from exc
    if not file_path.is_file():
        raise Http404
    content_type = (
        {
            ".webp": "image/webp",
            ".woff2": "font/woff2",
            ".svg": "image/svg+xml",
        }.get(file_path.suffix.lower())
        or mimetypes.guess_type(file_path.name)[0]
        or "application/octet-stream"
    )
    response = HttpResponse(file_path.read_bytes(), content_type=content_type)
    response["Cache-Control"] = "public, max-age=604800, immutable"
    return response


def site_data(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)
    from .serializers import build_site_data

    return JsonResponse(build_site_data())


def robots_txt(request):
    content = "\n".join(
        [
            "User-agent: *",
            "Disallow: /admin/",
            "Disallow: /api/",
            "Disallow: /en/admin/",
            f"Sitemap: {BASE_URL}/sitemap.xml",
            "Crawl-delay: 10",
            "",
            "User-agent: GPTBot",
            "Disallow: /",
            "",
            "User-agent: CCBot",
            "Disallow: /",
            "",
            "User-agent: ClaudeBot",
            "Disallow: /",
            "",
        ]
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")

import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode

from .content import CATEGORIES, SERVICES, UI, localize
from .models import Project

REGISTRY_PATH = Path(__file__).parent / "data" / "portfolio_projects.json"
BASE_URL = "https://rexileer.ru"


@lru_cache(maxsize=1)
def registry():
    return {
        item["slug"]: item
        for item in json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["projects"]
    }


def public_path(path, lang):
    return f"/en{path}" if lang == "en" else path


def present_project(project, lang):
    source = registry().get(project.slug, {})
    categories = source.get("categories", ["backend"])
    related = [
        service
        for service in SERVICES
        if project.slug in service["projects"]
        or {
            "python-backend": "backend",
            "telegram-bots": "telegram",
            "parsers-automation": "parsing",
            "ai-rag": "ai",
        }[service["slug"]]
        in categories
    ]
    media_lookup = {
        item.get("source_url", item["url"]): item
        for item in source.get("media_assets", [])
    }
    cover = source.get("cover_asset", {})
    if project.cover_image_url != cover.get("url"):
        cover = {"url": project.cover_image_url, "width": 1600, "height": 900}
    if cover.get("url", "").startswith("https://images.unsplash.com/"):
        cover = {}
    media = []
    for item in project.media.all():
        asset = media_lookup.get(item.url, {})
        caption = getattr(item, f"caption_{lang}")
        if asset.get("source_url") and caption == source.get(f"title_{lang}"):
            caption = asset.get(f"caption_{lang}", caption)
        media.append(
            {
                **asset,
                "url": asset.get("url", item.url),
                "type": item.media_type,
                "title": getattr(item, f"title_{lang}"),
                "caption": caption,
                "note": asset.get(f"note_{lang}", ""),
                "width": asset.get("width", 1600),
                "height": asset.get("height", 900),
                "srcset": image_srcset(asset),
            }
        )
    media = [item for item in media if item["url"] != cover.get("url")]
    return {
        "id": project.slug,
        "url": public_path(f"/projects/{project.slug}/", lang),
        "title": getattr(project, f"title_{lang}"),
        "description": getattr(project, f"description_{lang}"),
        "detail": getattr(project, f"detail_{lang}"),
        "problem": getattr(project, f"problem_{lang}"),
        "solution": getattr(project, f"solution_{lang}"),
        "result": getattr(project, f"result_{lang}"),
        "card_problem": source.get(f"card_problem_{lang}")
        or getattr(project, f"problem_{lang}"),
        "card_solution": source.get(f"card_solution_{lang}")
        or getattr(project, f"solution_{lang}"),
        "card_result": source.get(f"card_result_{lang}")
        or getattr(project, f"result_{lang}"),
        "features": source.get(f"features_{lang}", []),
        "flow": source.get(f"flow_{lang}", []),
        "flow_note": source.get(f"flow_note_{lang}", ""),
        "role": getattr(project, f"role_{lang}"),
        "featured": project.featured,
        "tags": [
            {"парсинг": "Parsing", "внешние API": "External APIs"}.get(tag, tag)
            if lang == "en"
            else tag
            for tag in project.tags
            if tag not in ("Нужен аудит", "Нужно уточнить")
        ],
        "highlights": [
            item if isinstance(item, dict) else {"title": item, "text": ""}
            for item in (
                source.get("showcase_en", []) if lang == "en" else project.highlights
            )
        ]
        if project.slug != "real-estate-parser"
        else [],
        "cover": {
            **cover,
            "alt": getattr(project, f"cover_alt_{lang}")
            or getattr(project, f"title_{lang}"),
            "srcset": image_srcset(cover),
            "note": cover.get(f"note_{lang}", ""),
        },
        "media": media,
        "categories": categories,
        "category_ids": " ".join(categories),
        "category_label": next(
            localize(category["label"], lang)
            for category in CATEGORIES
            if category["id"] == categories[0]
        ),
        "services": [present_service(service, lang) for service in related],
        "links": [link for link in project.links if link.get("public") is True],
    }


def image_srcset(asset):
    if not asset.get("url") or not asset.get("variants"):
        return ""
    variants = [*asset["variants"], {"url": asset["url"], "width": asset["width"]}]
    return ", ".join(f"{item['url']} {item['width']}w" for item in variants)


def present_service(service, lang):
    return {
        **localize(service, lang),
        "url": public_path(f"/services/{service['slug']}/", lang),
    }


def page_context(request, lang):
    lang = lang if lang in ("ru", "en") else "ru"
    path = request.path
    base_path = path[3:] if path.startswith("/en/") else path
    language_url = public_path(base_path, "ru" if lang == "en" else "en")
    category = request.GET.get("category", "")
    if base_path in ("/projects/", "/work/") and category in {
        c["id"] for c in CATEGORIES
    }:
        language_url += "?" + urlencode({"category": category})
    return {
        "lang": lang,
        "ui": localize(UI, lang),
        "categories": localize(CATEGORIES, lang),
        "services": [present_service(item, lang) for item in SERVICES],
        "home_url": public_path("/", lang),
        "services_url": public_path("/services/", lang),
        "projects_url": public_path("/projects/", lang),
        "work_url": public_path("/work/", lang),
        "canonical": BASE_URL + public_path(base_path, lang),
        "ru_url": BASE_URL + base_path,
        "en_url": BASE_URL + public_path(base_path, "en"),
        "language_url": language_url,
        "og_image": BASE_URL + "/assets/social-card.png",
    }


def published_projects(lang):
    return [
        present_project(project, lang)
        for project in Project.objects.filter(status=Project.Status.PUBLISHED)
        .prefetch_related("media")
        .order_by("order", "slug")
    ]


def structured_data(context, kind="WebPage", extra=None):
    payload = {
        "@context": "https://schema.org",
        "@type": kind,
        "name": context["title"],
        "description": context["description"],
        "url": context["canonical"],
        "inLanguage": context["lang"],
        "isPartOf": {"@type": "WebSite", "name": "Rexileer", "url": BASE_URL},
    }
    if extra:
        payload.update(extra)
    # Safe for embedding JSON in a raw-text script element, including admin text.
    return json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")

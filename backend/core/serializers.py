from collections import defaultdict

from .models import Project, SiteText, Skill


def _nested_dict():
    return defaultdict(_nested_dict)


def _set_nested(d, path, value):
    parts = path.split(".")
    for p in parts[:-1]:
        d = d[p]
    d[parts[-1]] = value


def _default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: _default_to_regular(v) for k, v in d.items()}
    return d


def build_copy():
    copy_en = _nested_dict()
    copy_ru = _nested_dict()
    for st in SiteText.objects.all():
        if st.lang == "en":
            _set_nested(copy_en, st.key, st.value)
        else:
            _set_nested(copy_ru, st.key, st.value)
    return {
        "en": _default_to_regular(dict(copy_en)),
        "ru": _default_to_regular(dict(copy_ru)),
    }


def build_skills():
    en = [s.text for s in Skill.objects.filter(lang="en").order_by("order")]
    ru = [s.text for s in Skill.objects.filter(lang="ru").order_by("order")]
    return {"en": en, "ru": ru}


def build_projects():
    out = []
    projects = (
        Project.objects.filter(status=Project.Status.PUBLISHED)
        .prefetch_related("media")
        .order_by("order", "slug")
    )
    for p in projects:
        source_group = {
            "BOTTEC": "commercial",
            "Сторонние и ТЗ": "external",
            "Пет-проекты": "personal",
        }.get(p.source_group, "other")
        public_links = [link for link in (p.links or []) if link.get("public") is True]
        out.append(
            {
                "id": p.slug,
                "detailUrl": f"/projects/{p.slug}/",
                "featured": p.featured,
                "sourceGroup": source_group,
                "title": {"en": p.title_en, "ru": p.title_ru},
                "description": {"en": p.description_en, "ru": p.description_ru},
                "detail": {"en": p.detail_en, "ru": p.detail_ru},
                "sections": {
                    "problem": {"en": p.problem_en, "ru": p.problem_ru},
                    "solution": {"en": p.solution_en, "ru": p.solution_ru},
                    "result": {"en": p.result_en, "ru": p.result_ru},
                },
                "role": {"en": p.role_en, "ru": p.role_ru},
                "cover": {
                    "url": p.cover_image_url,
                    "alt": {"en": p.cover_alt_en, "ru": p.cover_alt_ru},
                },
                "videoUrl": p.video_url,
                "tags": p.tags or [],
                "highlights": p.highlights or [],
                "links": public_links,
                "media": [
                    {
                        "type": item.media_type,
                        "title": {"en": item.title_en, "ru": item.title_ru},
                        "url": item.url,
                        "thumbnailUrl": item.thumbnail_url,
                        "caption": {"en": item.caption_en, "ru": item.caption_ru},
                    }
                    for item in p.media.all()
                ],
            }
        )
    return out


def build_site_data():
    return {
        "copy": build_copy(),
        "skills": build_skills(),
        "projects": build_projects(),
    }

from collections import defaultdict
from .models import SiteText, Skill, Project


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
    return {"en": _default_to_regular(dict(copy_en)), "ru": _default_to_regular(dict(copy_ru))}


def build_skills():
    en = [s.text for s in Skill.objects.filter(lang="en").order_by("order")]
    ru = [s.text for s in Skill.objects.filter(lang="ru").order_by("order")]
    return {"en": en, "ru": ru}


def build_projects():
    out = []
    for p in Project.objects.all():
        out.append({
            "id": p.slug,
            "meta": {"en": p.meta_en, "ru": p.meta_ru},
            "title": {"en": p.title_en, "ru": p.title_ru},
            "description": {"en": p.description_en, "ru": p.description_ru},
            "tags": p.tags or [],
            "links": p.links or [],
        })
    return out


def build_site_data():
    return {
        "copy": build_copy(),
        "skills": build_skills(),
        "projects": build_projects(),
    }

import json
import os
from dataclasses import dataclass
from json import JSONDecodeError

from django.utils import timezone
from django.utils.text import slugify

from core.models import AIProviderConfig, ProjectDraft

DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


@dataclass(frozen=True)
class GeneratedPortfolio:
    model: str
    data: dict


def generate_portfolio_draft(draft: ProjectDraft) -> GeneratedPortfolio:
    config = draft.ai_config or AIProviderConfig.get_default()
    if config and config.api_key:
        generated = _generate_with_provider(draft, config)
    else:
        generated = _generate_locally(draft)
    _apply_generated_data(draft, generated)
    return generated


def _generate_with_provider(
    draft: ProjectDraft, config: AIProviderConfig
) -> GeneratedPortfolio:
    from openai import OpenAI

    kwargs = {"api_key": config.api_key}
    if config.provider == AIProviderConfig.Provider.OPENROUTER:
        kwargs["base_url"] = "https://openrouter.ai/api/v1"
    if config.base_url:
        kwargs["base_url"] = config.base_url
    client = OpenAI(**kwargs)
    model = config.effective_model or DEFAULT_MODEL
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Return only valid JSON for a bilingual portfolio draft.",
            },
            {"role": "user", "content": _build_prompt(draft)},
        ],
        response_format={"type": "json_object"},
    )
    data = _extract_json(completion.choices[0].message.content or "{}")
    return GeneratedPortfolio(model=model, data=data)


def _generate_locally(draft: ProjectDraft) -> GeneratedPortfolio:
    title = _first_line(draft.prompt) or "Portfolio Project"
    slug = slugify(draft.slug or title) or f"project-{draft.pk or 'draft'}"
    context = draft.context.strip()
    summary = draft.prompt.strip()
    if len(summary) > 260:
        summary = summary[:257].rstrip() + "..."

    detail_ru = "\n\n".join(
        part
        for part in [
            draft.prompt.strip(),
            context and f"Контекст и требования: {context}",
            "Черновик создан локально. Добавьте активную AI-конфигурацию в админке, чтобы получать полноценную AI-генерацию.",
        ]
        if part
    )
    detail_en = "\n\n".join(
        part
        for part in [
            f"Project notes: {draft.prompt.strip()}",
            context and f"Context and constraints: {context}",
            "This draft was generated locally. Add an enabled AI provider config in admin to enable full AI generation.",
        ]
        if part
    )
    data = {
        "slug": slug,
        "title_en": title,
        "title_ru": title,
        "meta_en": "Draft",
        "meta_ru": "Черновик",
        "summary_en": summary,
        "summary_ru": summary,
        "detail_en": detail_en,
        "detail_ru": detail_ru,
        "problem_en": "Manual preparation of portfolio copy takes too much time.",
        "problem_ru": "Ручная подготовка портфолио занимает слишком много времени.",
        "solution_en": "Structure the project as an editable draft, then publish it after review.",
        "solution_ru": "Собрать проект в редактируемый черновик и опубликовать после проверки.",
        "result_en": "A reusable portfolio entry ready for admin editing.",
        "result_ru": "Готовая запись портфолио, которую можно быстро доработать в админке.",
        "role_en": "Backend developer",
        "role_ru": "Backend-разработчик",
        "year": str(timezone.now().year),
        "tags": _guess_tags(draft.prompt),
        "links": [],
    }
    return GeneratedPortfolio(model="local-template", data=data)


def _build_prompt(draft: ProjectDraft) -> str:
    return f"""
You are helping a Python backend developer maintain a bilingual portfolio.
Generate a concise, production-ready project portfolio draft from the notes.

Return only valid JSON with these keys:
slug, title_en, title_ru, meta_en, meta_ru, summary_en, summary_ru,
detail_en, detail_ru, problem_en, problem_ru, solution_en, solution_ru,
result_en, result_ru, role_en, role_ru, year, tags, links.

Rules:
- Russian fields must be natural Russian, English fields natural English.
- tags must be a JSON array of short technology tags.
- links must be a JSON array in this shape:
  {{"type": "github|demo|telegram|site", "href": "https://...", "label": {{"en": "...", "ru": "..."}}}}
- Keep summary fields short enough for project cards.
- Keep detail fields suitable for a dedicated project page.

Project notes:
{draft.prompt}

Extra context:
{draft.context}
""".strip()


def _extract_json(text: str) -> dict:
    value = text.strip()
    if value.startswith("```"):
        value = value.strip("`")
        value = value.removeprefix("json").strip()
    try:
        data = json.loads(value)
    except JSONDecodeError as exc:
        raise ValueError("AI response is not valid JSON") from exc
    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object")
    return data


def _apply_generated_data(draft: ProjectDraft, generated: GeneratedPortfolio):
    data = generated.data
    draft.slug = data.get("slug") or draft.slug
    for field in [
        "title_en",
        "title_ru",
        "meta_en",
        "meta_ru",
        "summary_en",
        "summary_ru",
        "detail_en",
        "detail_ru",
        "problem_en",
        "problem_ru",
        "solution_en",
        "solution_ru",
        "result_en",
        "result_ru",
        "role_en",
        "role_ru",
        "year",
        "cover_image_url",
        "video_url",
    ]:
        value = data.get(field)
        if value:
            setattr(draft, field, value)
    draft.tags = data.get("tags") or draft.tags or []
    draft.links = data.get("links") or draft.links or []
    draft.ai_model = generated.model
    draft.ai_response = data
    draft.generated_at = timezone.now()
    draft.status = ProjectDraft.Status.GENERATED
    draft.save()


def _first_line(value: str) -> str:
    for line in value.splitlines():
        line = line.strip(" #-")
        if line:
            return line[:120]
    return ""


def _guess_tags(value: str) -> list[str]:
    known = [
        "Python",
        "Django",
        "FastAPI",
        "Telegram",
        "Aiogram",
        "PostgreSQL",
        "Redis",
        "Docker",
        "Celery",
        "OpenAI",
    ]
    lower = value.lower()
    tags = [tag for tag in known if tag.lower() in lower]
    return tags or ["Python", "Django"]

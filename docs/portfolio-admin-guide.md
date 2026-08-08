# Portfolio Admin Guide

## Admin Workflow

1. Open `/admin/`.
2. Manage published portfolio entries in `Core -> Projects`.
3. Add screenshots, GIFs, or videos through the `Project media` inline on a project.
4. Create rough AI inputs in `Core -> Project drafts`.
5. Select a draft and run `Generate portfolio copy with AI`.
6. Review and edit the generated fields.
7. Select the draft and run `Publish selected drafts`.
8. The public site reads only projects with status `Published`.

The public routes are:

- `/` — sales-focused landing page and selected cases;
- `/projects/` — all featured, full-size cases;
- `/projects/<slug>/` — an individual case study;
- `/work/` — the compact archive of additional projects.

## Versioned project registry

`backend/core/data/portfolio_projects.json` is the canonical, reviewable import
file for projects supplied through chat or a spreadsheet. Run the following after
changing it:

```text
python manage.py sync_portfolio_registry
```

The deployment entrypoint runs this command automatically. It updates copy,
classification, tags, links, and ordering, but preserves custom cover images,
manually added media, private AI notes, and the original publication date.

Client names, project state, year, and unapproved repository URLs are admin-only
metadata and are not included in the public API. To publish a demo link later,
add `"public": true` to that link in the registry after confirming that the
target is intentionally public.

## AI providers

Open `Core -> AI provider configs`.

- Choose `OpenAI` or `OpenRouter`.
- Pick a model from the dropdown.
- Use `custom_model` only when a model is not listed yet.
- Paste the API key into `api_key`.
- Enable the profile and mark one profile as default.

Recommended cheap OpenAI model:

```text
gpt-4o-mini
```

If no key is configured, the admin action still creates a local structured draft so the publishing workflow remains usable.

## Project Fields

- Card: `meta`, `title`, `description`, `tags`, `links`, `cover_image_url`.
- Detail page: `detail`, `problem`, `solution`, `result`, `role`, `year`.
- Media: image, GIF, and video URLs with captions.
- Classification: `source_group`, `client`, `project_state`, `featured`.
- Publication: `status`, `published_at`, `order`.

## Telegram Drafts

`Telegram post drafts` are prepared for the future bot integration. They can already store channel-ready text and link it to a project, but sending is not wired yet.

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
- Publication: `status`, `featured`, `published_at`.

## Telegram Drafts

`Telegram post drafts` are prepared for the future bot integration. They can already store channel-ready text and link it to a project, but sending is not wired yet.

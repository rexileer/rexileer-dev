import json
from pathlib import Path

from core.models import Project, ProjectMedia
from django.core.management.base import BaseCommand
from django.utils import timezone

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "portfolio_projects.json"

LEGACY_SLUGS = {
    "ai-consultant",
    "ai_miniapp_bot",
    "avito-parsing-microservice",
    "meat-bot",
    "parser-daa-bot",
    "scalping-bot",
    "search-lead-generation-bot",
    "steps-bot",
    "telegram-channel",
}


class Command(BaseCommand):
    help = "Synchronize the published portfolio from the versioned project registry."

    def handle(self, *args, **options):
        payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        synced = 0

        for item in payload["projects"]:
            meta = " · ".join(
                part for part in (item["client"], item["status_label"]) if part
            )
            defaults = {
                "status": Project.Status.PUBLISHED,
                "featured": item["featured"],
                "source_group": item["source"],
                "client": item["client"],
                "project_state": item["status_label"],
                "meta_ru": meta,
                "meta_en": meta,
                "title_ru": item["title_ru"],
                "title_en": item["title_en"] or item["title_ru"],
                "description_ru": item["description_ru"],
                "description_en": item["description_en"] or item["description_ru"],
                "detail_ru": item["detail_ru"],
                "detail_en": item["detail_ru"],
                "problem_ru": item["problem_ru"],
                "problem_en": item["problem_ru"],
                "solution_ru": item["solution_ru"],
                "solution_en": item["solution_ru"],
                "result_ru": item["result_ru"],
                "result_en": item["result_ru"],
                "role_ru": item["role_ru"][:160],
                "role_en": item["role_ru"][:160],
                "year": item["year"],
                "tags": item["tags"],
                "highlights": item["showcase"],
                "links": item["links"],
                "order": item["order"],
                "updated_at": timezone.now(),
            }
            project, created = Project.objects.update_or_create(
                slug=item["slug"], defaults=defaults
            )

            preserved_fields = []
            if (
                created
                or not project.cover_image_url
                or project.cover_image_url.startswith("https://images.unsplash.com/")
            ):
                project.cover_image_url = item["cover_image_url"]
                project.cover_alt_ru = item["cover_alt_ru"]
                project.cover_alt_en = item["cover_alt_ru"]
                preserved_fields.extend(
                    ["cover_image_url", "cover_alt_ru", "cover_alt_en"]
                )
            if project.published_at is None:
                project.published_at = timezone.now()
                preserved_fields.append("published_at")
            if preserved_fields:
                project.save(update_fields=preserved_fields)

            for order, screenshot in enumerate(item["screenshots"]):
                ProjectMedia.objects.update_or_create(
                    project=project,
                    url=screenshot,
                    defaults={
                        "media_type": ProjectMedia.MediaType.IMAGE,
                        "title_ru": f"Экран проекта {order + 1}",
                        "title_en": f"Project screen {order + 1}",
                        "caption_ru": item["title_ru"],
                        "caption_en": item["title_en"],
                        "order": order,
                    },
                )
            synced += 1

        Project.objects.filter(slug__in=LEGACY_SLUGS).update(
            status=Project.Status.ARCHIVED, updated_at=timezone.now()
        )
        self.stdout.write(self.style.SUCCESS(f"Synchronized {synced} projects."))

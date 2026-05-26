from django.test import TestCase

from .models import (
    AIProviderConfig,
    Project,
    ProjectDraft,
    ProjectMedia,
    TelegramPostDraft,
    VisitLog,
)
from .serializers import build_projects
from .services.ai_portfolio import generate_portfolio_draft


class PortfolioWorkflowTests(TestCase):
    def test_published_projects_are_serialized_with_media_and_detail(self):
        project = Project.objects.create(
            slug="demo-crm",
            status=Project.Status.PUBLISHED,
            meta_en="CRM",
            meta_ru="CRM",
            title_en="Demo CRM",
            title_ru="Демо CRM",
            description_en="Short summary",
            description_ru="Короткое описание",
            detail_en="Long project story",
            detail_ru="Подробное описание проекта",
            problem_en="Manual operations",
            solution_en="Automated workflow",
            result_en="Faster delivery",
            role_en="Backend developer",
            year="2026",
            cover_image_url="https://example.com/cover.jpg",
            tags=["Django", "Docker"],
            links=[
                {
                    "type": "github",
                    "href": "https://github.com/rexileer/demo",
                    "label": {"en": "GitHub", "ru": "GitHub"},
                }
            ],
        )
        ProjectMedia.objects.create(
            project=project,
            media_type=ProjectMedia.MediaType.IMAGE,
            url="https://example.com/screen.png",
            caption_en="Admin screen",
            caption_ru="Экран админки",
        )
        Project.objects.create(
            slug="hidden",
            status=Project.Status.DRAFT,
            title_en="Hidden",
            title_ru="Скрытый",
        )

        data = build_projects()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "demo-crm")
        self.assertEqual(data[0]["detail"]["en"], "Long project story")
        self.assertEqual(data[0]["sections"]["problem"]["en"], "Manual operations")
        self.assertEqual(data[0]["media"][0]["url"], "https://example.com/screen.png")
        self.assertEqual(data[0]["detailUrl"], "#project/demo-crm")

    def test_project_draft_publishes_to_project(self):
        draft = ProjectDraft.objects.create(
            slug="ai-project",
            prompt="Telegram bot with Django CRM",
            title_en="AI Project",
            title_ru="ИИ-проект",
            meta_en="Automation",
            meta_ru="Автоматизация",
            summary_en="Short EN",
            summary_ru="Short RU",
            detail_en="Detailed EN",
            detail_ru="Detailed RU",
            tags=["Django", "Telegram"],
            links=[],
        )

        project = draft.publish_to_project()

        self.assertEqual(project.slug, "ai-project")
        self.assertEqual(project.status, Project.Status.PUBLISHED)
        self.assertEqual(project.description_en, "Short EN")
        self.assertEqual(project.detail_ru, "Detailed RU")
        self.assertEqual(draft.status, ProjectDraft.Status.PUBLISHED)
        self.assertEqual(draft.published_project, project)

    def test_telegram_post_draft_can_be_attached_to_project(self):
        project = Project.objects.create(
            slug="tg-ready",
            title_en="TG Ready",
            title_ru="TG Ready",
        )

        draft = TelegramPostDraft.objects.create(
            project=project,
            title="Launch note",
            body="Draft text for channel",
            channel_hint="@rexileerdev",
        )

        self.assertEqual(draft.project, project)
        self.assertEqual(draft.status, TelegramPostDraft.Status.DRAFT)

    def test_ai_config_supports_provider_and_model_selection(self):
        config = AIProviderConfig.objects.create(
            name="OpenRouter free",
            provider=AIProviderConfig.Provider.OPENROUTER,
            model=AIProviderConfig.ModelChoice.OPENROUTER_LLAMA_FREE,
            custom_model="",
            api_key="",
            is_default=True,
        )
        draft = ProjectDraft.objects.create(
            ai_config=config,
            slug="provider-test",
            prompt="Django Telegram bot for factory operations",
        )

        generated = generate_portfolio_draft(draft)
        draft.refresh_from_db()

        self.assertEqual(draft.ai_config, config)
        self.assertEqual(generated.model, "local-template")
        self.assertEqual(draft.status, ProjectDraft.Status.GENERATED)
        self.assertIn("Django", draft.tags)


class VisitLoggingTests(TestCase):
    def test_browser_visit_to_homepage_is_logged(self):
        self.client.get(
            "/",
            HTTP_USER_AGENT=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
            REMOTE_ADDR="203.0.113.10",
        )

        visit = VisitLog.objects.get()
        self.assertEqual(visit.path, "/")
        self.assertEqual(visit.ip, "203.0.113.10")

    def test_scanner_homepage_request_is_not_logged(self):
        response = self.client.get(
            "/",
            HTTP_USER_AGENT="Python-urllib/3.12",
            REMOTE_ADDR="203.0.113.20",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(VisitLog.objects.count(), 0)

    def test_repeated_homepage_request_from_same_client_is_logged_once(self):
        headers = {
            "HTTP_USER_AGENT": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
            "REMOTE_ADDR": "203.0.113.40",
        }

        self.client.get("/", **headers)
        self.client.get("/", **headers)

        self.assertEqual(VisitLog.objects.count(), 1)

    def test_robots_txt_is_served_without_visit_log(self):
        response = self.client.get(
            "/robots.txt",
            HTTP_USER_AGENT="Googlebot/2.1",
            REMOTE_ADDR="203.0.113.30",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertIn("User-agent: *", response.content.decode())
        self.assertIn("Disallow: /admin/", response.content.decode())
        self.assertEqual(VisitLog.objects.count(), 0)

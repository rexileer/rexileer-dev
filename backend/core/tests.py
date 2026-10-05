import json

from django.core.management import call_command
from django.test import Client, TestCase

from .models import (
    AIProviderConfig,
    Project,
    ProjectDraft,
    ProjectMedia,
    SiteEvent,
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
        self.assertEqual(data[0]["detailUrl"], "/projects/demo-crm/")
        self.assertEqual(data[0]["links"], [])
        self.assertNotIn("client", data[0])
        self.assertNotIn("year", data[0])

    def test_project_routes_serve_the_portfolio_app(self):
        Project.objects.create(
            slug="demo-crm", title_ru="Демо CRM", title_en="Demo CRM"
        )
        self.assertEqual(self.client.get("/projects/").status_code, 200)
        self.assertEqual(self.client.get("/projects/demo-crm/").status_code, 200)
        self.assertEqual(self.client.get("/work/").status_code, 200)

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


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_portfolio_registry", verbosity=0)

    def test_service_pages_are_localized_and_have_server_rendered_metadata(self):
        slugs = ("python-backend", "telegram-bots", "parsers-automation", "ai-rag")
        titles = set()
        for lang, prefix in (("ru", ""), ("en", "/en")):
            for slug in slugs:
                with self.subTest(lang=lang, slug=slug):
                    path = f"{prefix}/services/{slug}/"
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 200)
                    html = response.content.decode()
                    self.assertIn(f'<html lang="{lang}">', html)
                    self.assertIn(
                        f'<link rel="canonical" href="https://rexileer.ru{path}"', html
                    )
                    self.assertIn('hreflang="ru"', html)
                    self.assertIn('hreflang="en"', html)
                    self.assertEqual(html.count("<h1"), 1)
                    self.assertIn("FAQPage", html)
                    self.assertIn('data-event="telegram_click"', html)
                    titles.add(response.context["title"])
                    if lang == "en":
                        self.assertNotIn("Обсудить задачу", html)
                        self.assertNotIn("Управление промптами", html)
                    json.loads(response.context["schema"])
        self.assertEqual(len(titles), 8)

    def test_unknown_projects_and_services_return_real_404(self):
        for path in (
            "/projects/missing/",
            "/services/missing/",
            "/en/projects/missing/",
        ):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 404)
            self.assertContains(response, 'content="noindex, follow"', status_code=404)

    def test_gallery_assets_and_original_easter_egg_are_in_html(self):
        response = self.client.get("/projects/ai-lead-scoring/")
        self.assertContains(response, "data-gallery")
        self.assertContains(response, "/assets/projects/ai-lead-scoring/")
        self.assertContains(response, "radiokp.ru/sites/default/files/")
        self.assertNotContains(response, "images.unsplash.com")
        self.assertNotContains(response, "BottecRu/")
        self.assertNotContains(response, "/site/assets/")

    def test_sitemap_contains_both_languages_and_published_projects(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://rexileer.ru/services/ai-rag/")
        self.assertContains(
            response, "https://rexileer.ru/en/projects/ai-lead-scoring/"
        )
        self.assertContains(self.client.get("/robots.txt"), "Sitemap:")

    def test_sync_preserves_custom_covers_media_and_publication_date(self):
        project = Project.objects.get(slug="ai-lead-scoring")
        published_at = project.published_at
        project.cover_image_url = "https://example.com/custom-cover.webp"
        project.save()
        media = project.media.first()
        media.caption_en = "Edited in admin"
        media.save()
        before = project.media.count()
        call_command("sync_portfolio_registry", verbosity=0)
        project.refresh_from_db()
        media.refresh_from_db()
        self.assertEqual(
            project.cover_image_url, "https://example.com/custom-cover.webp"
        )
        self.assertEqual(project.published_at, published_at)
        self.assertEqual(media.caption_en, "Edited in admin")
        self.assertEqual(project.media.count(), before)
        from core.presentation import present_project

        self.assertIn(
            "Edited in admin",
            [item["caption"] for item in present_project(project, "en")["media"]],
        )

    def test_all_cases_have_complete_copy_and_no_empty_decision_cards(self):
        from core.presentation import present_project, registry

        for project in Project.objects.filter(status=Project.Status.PUBLISHED):
            source = registry()[project.slug]
            for lang in ("ru", "en"):
                with self.subTest(project=project.slug, lang=lang):
                    case = present_project(project, lang)
                    self.assertEqual(case["role"], source[f"role_{lang}"])
                    for field in ("card_problem", "card_solution", "card_result"):
                        self.assertTrue(case[field].endswith((".", "!", "?")))
                        self.assertNotIn("…", case[field])
                    for decision in case["highlights"]:
                        self.assertTrue(decision["title"].strip())
                        self.assertTrue(decision["text"].strip())
                    self.assertFalse(case["features"] and case["highlights"])
                    self.assertNotIn("добавить скриншот", case["result"].lower())
        self.assertGreater(
            len(Project.objects.get(slug="hr-corporate-platform").role_ru), 160
        )

    def test_language_switch_keeps_only_known_category_without_polluting_canonical(
        self,
    ):
        for path, alternate in (
            ("/projects/", "/en/projects/"),
            ("/en/work/", "/work/"),
        ):
            response = self.client.get(path, {"category": "ai", "private": "discard"})
            self.assertEqual(
                response.context["language_url"], alternate + "?category=ai"
            )
            self.assertEqual(
                response.context["canonical"], "https://rexileer.ru" + path
            )
            self.assertNotIn("?", response.context["ru_url"])
        invalid = self.client.get("/projects/", {"category": "unexpected"})
        self.assertEqual(invalid.context["language_url"], "/en/projects/")

    def test_demo_covers_are_labelled_and_can_open_at_full_resolution(self):
        for slug in ("hr-corporate-platform", "bozon-medpreds"):
            response = self.client.get(f"/projects/{slug}/")
            self.assertContains(response, "cover-zoom")
            self.assertContains(response, "демонстрационные")
        response = self.client.get("/projects/payment-broadcast-bot/")
        self.assertContains(response, 'class="feature-list"')
        self.assertNotContains(response, 'class="highlight-item"')

    def test_screenshot_mirrors_keep_source_records_without_gallery_duplicates(self):
        from core.presentation import present_project, registry

        project = Project.objects.get(slug="wallet-risk-scorer")
        sources = registry()[project.slug]["screenshots"]
        call_command("sync_portfolio_registry", verbosity=0)
        self.assertEqual(set(project.media.values_list("url", flat=True)), set(sources))
        for lang in ("ru", "en"):
            case = present_project(project, lang)
            self.assertTrue(case["cover"]["url"].startswith("/assets/projects/"))
            self.assertEqual(len(case["media"]), 1)
            self.assertEqual(case["media"][0]["width"], 605)
            self.assertEqual(case["media"][0]["height"], 385)
            self.assertNotEqual(case["cover"]["url"], case["media"][0]["url"])


class SiteEventTests(TestCase):
    def test_event_requires_csrf_and_stores_only_allowed_fields(self):
        client = Client(enforce_csrf_checks=True)
        data = {"name": "telegram_click", "location": "hero", "path": "/", "lang": "ru"}
        self.assertEqual(client.post("/api/events/", data).status_code, 403)
        client.get("/")
        data["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
        self.assertEqual(client.post("/api/events/", data).status_code, 204)
        self.assertEqual(SiteEvent.objects.get().location, "hero")
        data["name"] = "unexpected"
        self.assertEqual(client.post("/api/events/", data).status_code, 400)
        self.assertEqual(SiteEvent.objects.count(), 1)

    def test_event_endpoint_does_not_accept_get_or_private_query_strings(self):
        self.assertEqual(self.client.get("/api/events/").status_code, 405)
        response = self.client.post(
            "/api/events/",
            {
                "name": "telegram_click",
                "location": "hero",
                "path": "/?password=hidden",
                "lang": "en",
            },
        )
        self.assertEqual(response.status_code, 400)

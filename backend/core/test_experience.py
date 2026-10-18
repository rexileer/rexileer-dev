from django.core.management import call_command
from django.test import TestCase
from django.utils.html import escape

from .models import Project


class PortfolioExperienceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_portfolio_registry", verbosity=0)

    def test_home_exposes_honest_complete_walkthroughs_and_early_case_evidence(self):
        for prefix in ("", "/en"):
            response = self.client.get(prefix + "/")
            self.assertEqual(response.status_code, 200)
            scenarios = response.context["scenarios"]
            self.assertEqual(len(scenarios), 3)
            for scenario in scenarios:
                self.assertEqual(len(scenario["steps"]), 4)
                self.assertTrue(scenario["input"] and scenario["result"])
                self.assertEqual(self.client.get(scenario["case_url"]).status_code, 200)
            html = response.content.decode()
            self.assertLess(html.index('id="cases"'), html.index('id="services"'))
            self.assertNotIn("Без выдуманных", html)
            self.assertContains(response, 'class="lab-scenario"', count=3)
            self.assertContains(
                response, 'data-event="telegram_click" data-location="hero"'
            )
            self.assertContains(response, "radiokp.ru/")

    def test_study_template_preserves_every_case_fact_and_original_media_link(self):
        for project in Project.objects.filter(status=Project.Status.PUBLISHED):
            for prefix, lang in (("", "ru"), ("/en", "en")):
                with self.subTest(project=project.slug, lang=lang):
                    response = self.client.get(f"{prefix}/projects/{project.slug}/")
                    self.assertEqual(response.status_code, 200)
                    for field in ("problem", "role", "solution", "result"):
                        self.assertContains(
                            response, escape(getattr(project, f"{field}_{lang}"))
                        )
                    case = response.context["project"]
                    if case["cover"]["url"]:
                        self.assertContains(response, case["cover"]["url"])
                    for media in case["media"]:
                        self.assertContains(response, media["url"])
                    self.assertContains(
                        response, 'data-event="email_click" data-location="project"'
                    )

    def test_lab_has_localized_fallback_and_versioned_browser_modules(self):
        for prefix in ("", "/en"):
            response = self.client.get(prefix + "/")
            self.assertEqual(response.context["scenarios"][0]["id"], "collection")
            self.assertContains(response, "data-lab-fallback", count=3)
            self.assertContains(response, "data-batch-size")
            self.assertContains(response, "data-confirmed")
            self.assertContains(response, "data-source")
            self.assertContains(response, 'id="lab-copy"')
            self.assertContains(response, "process-lab.mjs?v=")
            for kind in ("collection", "access", "knowledge"):
                self.assertContains(response, f'href="#lab-{kind}"')
            self.assertNotContains(response, "https://t.me/+")
        for name in ("lab-model", "process-lab"):
            response = self.client.get(f"/assets/js/{name}.mjs?v=verification")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "text/javascript")

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import OperationalError
from django.test import Client, TestCase
from django.utils import timezone

from .analytics import COOKIE, EVENT_LIMIT, VIEW_LIMIT, cookie_context
from .analytics_report import acquisition_report
from .models import Project, SiteEvent, VisitLog

BROWSER = {
    "HTTP_USER_AGENT": "Mozilla/5.0 Chrome/120 Safari/537.36",
    "REMOTE_ADDR": "203.0.113.7",
}
EVENT = {
    "name": "telegram_click",
    "location": "service",
    "path": "/services/ai-rag/",
    "lang": "ru",
}


class AcquisitionTests(TestCase):
    def setUp(self):
        self.browser = Client(**BROWSER)

    def test_first_touch_follows_service_click_and_test_data_stay_separate(self):
        self.browser.get(
            "/?utm_source=telegram&utm_medium=profile&utm_campaign=oct17&email=private@example.com",
            HTTP_REFERER="https://t.me/channel?private=secret",
            HTTP_X_REXILEER_ANALYTICS="test",
        )
        self.browser.get("/services/ai-rag/")
        self.browser.post("/api/events/", EVENT)
        report = acquisition_report(7, True)
        self.assertEqual(
            report["totals"],
            {"views": 2, "entries": 1, "telegram": 1, "email": 0, "cases": 0},
        )
        source = report["sources"][0]
        self.assertEqual(
            (source["utm_source"], source["utm_campaign"], source["referrer_domain"]),
            ("telegram", "oct17", "t.me"),
        )
        event = SiteEvent.objects.get()
        self.assertEqual(event.entry_path, "/")
        self.assertEqual(event.utm_source, "telegram")
        self.assertEqual(acquisition_report()["totals"]["views"], 0)
        self.assertIsNone(VisitLog.objects.first().ip)
        self.assertEqual(VisitLog.objects.first().user_agent, "")
        self.assertNotIn("private", str(source))

    def test_all_public_templates_and_languages_count_only_successful_html(self):
        Project.objects.create(
            slug="analytics-case", title_ru="Кейс", title_en="Case", status="published"
        )
        routes = [
            "/",
            "/services/",
            "/projects/",
            "/work/",
            "/privacy/",
            "/services/python-backend/",
            "/services/telegram-bots/",
            "/services/parsers-automation/",
            "/services/ai-rag/",
            "/projects/analytics-case/",
        ]
        for prefix in ("", "/en"):
            for path in routes:
                self.assertEqual(self.browser.get(prefix + path).status_code, 200)
        before = VisitLog.objects.count()
        for path in (
            "/admin/",
            "/api/site-data/",
            "/styles.css",
            "/assets/favicon.svg",
            "/robots.txt",
            "/sitemap.xml",
            "/missing/",
            "/projects/missing/",
        ):
            self.browser.get(path)
        self.browser.head("/")
        self.assertEqual(VisitLog.objects.count(), before)
        self.assertEqual(before, 20)

    def test_bad_tags_referrers_and_forged_cookie_are_not_saved(self):
        self.browser.cookies[COOKIE] = "forged"
        self.browser.get(
            "/",
            {
                "utm_source": "someone@example.com",
                "utm_medium": "https://example.com/",
                "utm_campaign": "x" * 65,
            },
            HTTP_REFERER="https://rexileer.ru/?secret=hidden",
        )
        view = VisitLog.objects.get()
        self.assertEqual(
            (view.utm_source, view.utm_medium, view.utm_campaign, view.referrer_domain),
            ("", "", "", ""),
        )
        self.assertTrue(view.is_entry)

    def test_cookie_does_not_trust_the_existing_application_signing_key(self):
        from django.core import signing
        from django.test import RequestFactory

        from .analytics import COOKIE_SALT

        request = RequestFactory().get("/")
        request.COOKIES[COOKIE] = signing.dumps(
            {"entry_path": "/", "utm_source": "forged"}, salt=COOKIE_SALT
        )
        self.assertEqual(cookie_context(request), {})

    def test_new_campaign_or_external_arrival_restarts_fixed_window(self):
        self.browser.get("/?utm_source=telegram&utm_campaign=one")
        self.browser.get("/en/services/ai-rag/")
        self.browser.get("/services/ai-rag/?utm_source=github&utm_campaign=two")
        self.assertEqual(VisitLog.objects.filter(is_entry=True).count(), 2)
        self.assertEqual(VisitLog.objects.first().utm_source, "github")
        from django.test import RequestFactory

        request = RequestFactory().get("/")
        request.COOKIES[COOKIE] = self.browser.cookies[COOKIE].value
        with patch(
            "django.core.signing.time.time",
            return_value=timezone.now().timestamp() + 1801,
        ):
            self.assertEqual(cookie_context(request), {})

    def test_scanners_staff_optouts_and_checks_do_not_enter_live_report(self):
        for headers in (
            {"HTTP_USER_AGENT": "HeadlessChrome/120"},
            {"HTTP_DNT": "1"},
            {"HTTP_SEC_GPC": "1"},
            {"HTTP_X_REXILEER_ANALYTICS": "exclude"},
        ):
            self.browser.get("/", **headers)
            self.browser.post("/api/events/", EVENT, **headers)
        staff = get_user_model().objects.create_user("staff", is_staff=True)
        self.browser.force_login(staff)
        self.browser.get("/")
        self.browser.post("/api/events/", EVENT)
        self.assertEqual(VisitLog.objects.count(), 0)
        self.assertEqual(SiteEvent.objects.count(), 0)

    def test_frequency_limits_and_duplicate_click_suppression(self):
        self.browser.get("/")
        key = VisitLog.objects.get().client_key
        VisitLog.objects.bulk_create(
            [
                VisitLog(path="/", client_key=key, version=1)
                for _ in range(VIEW_LIMIT - 1)
            ]
        )
        self.browser.get("/")
        self.assertEqual(VisitLog.objects.count(), VIEW_LIMIT)
        self.browser.post("/api/events/", EVENT)
        self.browser.post("/api/events/", EVENT)
        self.assertEqual(SiteEvent.objects.count(), 1)
        SiteEvent.objects.bulk_create(
            [
                SiteEvent(**EVENT, client_key=key, version=1)
                for _ in range(EVENT_LIMIT - 1)
            ]
        )
        self.browser.post("/api/events/", {**EVENT, "name": "email_click"})
        self.assertEqual(SiteEvent.objects.count(), EVENT_LIMIT)

    def test_event_path_and_language_are_allowlisted(self):
        for path in (
            "/admin/",
            "/missing/",
            "/services/missing/",
            "/?email=secret",
            "//evil.test/",
        ):
            self.assertEqual(
                self.browser.post("/api/events/", {**EVENT, "path": path}).status_code,
                400,
            )
        self.assertEqual(
            self.browser.post("/api/events/", {**EVENT, "lang": "en"}).status_code, 400
        )

    def test_only_private_proxy_peer_can_supply_real_ip(self):
        from django.test import RequestFactory

        from .analytics import client_ip

        factory = RequestFactory()
        public = factory.get("/", REMOTE_ADDR="8.8.8.8", HTTP_X_REAL_IP="1.1.1.1")
        self.assertEqual(client_ip(public), "8.8.8.8")
        proxied = factory.get(
            "/",
            REMOTE_ADDR="172.17.0.1",
            HTTP_X_REAL_IP="8.8.8.8",
            HTTP_X_FORWARDED_FOR="1.1.1.1",
        )
        self.assertEqual(client_ip(proxied), "8.8.8.8")

    def test_analytics_write_failures_do_not_break_html_or_click_response(self):
        with patch(
            "core.analytics.VisitLog.objects.create",
            side_effect=OperationalError("private payload"),
        ):
            with self.assertLogs("core.middleware", level="WARNING") as output:
                self.assertEqual(self.browser.get("/").status_code, 200)
            self.assertNotIn("private payload", str(output.output))
        with patch(
            "core.analytics.SiteEvent.objects.create",
            side_effect=OperationalError("private payload"),
        ):
            self.assertEqual(self.browser.post("/api/events/", EVENT).status_code, 204)

    def test_report_periods_permissions_legacy_and_no_people_claims(self):
        user = get_user_model().objects.create_superuser("owner", "", "test-only")
        self.browser.force_login(user)
        VisitLog.objects.create(
            path="/", version=0, ip="203.0.113.2", user_agent="legacy"
        )
        old = VisitLog.objects.create(path="/", version=1)
        VisitLog.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=8)
        )
        self.assertEqual(acquisition_report(7)["totals"]["views"], 0)
        self.assertEqual(acquisition_report(30)["totals"]["views"], 1)
        response = self.browser.get("/admin/core/visitlog/?period=30&traffic=test")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Проверочные данные")
        self.assertContains(response, "не люди и не сессии")
        self.assertEqual(response.context["legacy_views"], 1)
        self.browser.logout()
        self.assertEqual(self.browser.get("/admin/core/visitlog/").status_code, 302)
        staff = get_user_model().objects.create_user("limited", is_staff=True)
        self.browser.force_login(staff)
        self.assertEqual(self.browser.get("/admin/core/visitlog/").status_code, 403)

    def test_retention_deletes_only_expired_analytics(self):
        project = Project.objects.create(slug="keep", title_ru="Кейс")
        expired = timezone.now() - timedelta(days=91)
        old_view = VisitLog.objects.create(
            path="/", ip="203.0.113.3", user_agent="legacy"
        )
        old_event = SiteEvent.objects.create(**EVENT)
        VisitLog.objects.filter(pk=old_view.pk).update(created_at=expired)
        SiteEvent.objects.filter(pk=old_event.pk).update(created_at=expired)
        current = VisitLog.objects.create(path="/", version=1)
        call_command("prune_analytics", verbosity=0)
        self.assertEqual(
            list(VisitLog.objects.values_list("pk", flat=True)), [current.pk]
        )
        self.assertEqual(SiteEvent.objects.count(), 0)
        self.assertTrue(Project.objects.filter(pk=project.pk).exists())

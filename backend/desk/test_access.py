from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from .models import LoginGuard
from .services import save_record


class AccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            settings.OWNER_USERNAME,
            password="Synthetic-owner-password-123",
            is_superuser=True,
        )
        save_record("task", {"title": "Synthetic private task"}, actor="test")

    def request(self, path, **kwargs):
        return self.client.get(
            path, secure=True, HTTP_HOST="desk.rexileer.ru", **kwargs
        )

    def test_anonymous_and_other_account_cannot_read_or_export(self):
        for route in [
            "/",
            "/records/task/",
            "/data/",
            "/data/export/",
            "/documents/",
            "/documents/1/preview/",
            "/documents/1/download/",
        ]:
            response = self.request(route)
            self.assertEqual(response.status_code, 302, route)
            self.assertNotContains(response, "Synthetic private task", status_code=302)
        nonowner = get_user_model().objects.create_user(
            "nonowner", password="Synthetic-nonowner-password", is_staff=True
        )
        self.client.force_login(nonowner)
        self.assertEqual(self.request("/data/export/").status_code, 403)

    def test_wrong_hosts_never_get_private_records(self):
        self.client.force_login(self.user)
        for host in ["rexileer.ru", "www.rexileer.ru", "attacker.invalid"]:
            response = self.client.get("/data/export/", secure=True, HTTP_HOST=host)
            self.assertEqual(response.status_code, 400)
            self.assertNotContains(response, "Synthetic private task", status_code=400)

    def test_owner_pages_export_and_cookie_isolation(self):
        self.client.post(
            "/login/",
            {
                "username": settings.OWNER_USERNAME,
                "password": "Synthetic-owner-password-123",
            },
            secure=True,
            HTTP_HOST="desk.rexileer.ru",
        )
        for route in [
            "/",
            "/calendar/",
            "/records/task/",
            "/records/task/new/",
            "/records/obligation/new/",
            "/records/addon/new/",
            "/records/email/new/",
            "/records/letter/new/",
            "/data/",
            "/documents/",
            "/documents/new/",
        ]:
            response = self.request(route)
            self.assertEqual(response.status_code, 200, route)
            self.assertIn("no-store", response["Cache-Control"])
        self.assertIn(
            "Synthetic private task", self.request("/data/export/").content.decode()
        )
        self.assertNotIn("/api/events/", self.request("/").content.decode())
        cookie = self.client.cookies[settings.SESSION_COOKIE_NAME]
        self.assertTrue(cookie["secure"])
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["domain"], "")
        self.assertEqual(cookie["samesite"], "Strict")

    def test_csrf_and_logout_are_real_and_next_is_safe(self):
        csrf = Client(enforce_csrf_checks=True)
        self.assertEqual(
            csrf.post(
                "/login/",
                {
                    "username": settings.OWNER_USERNAME,
                    "password": "Synthetic-owner-password-123",
                },
                secure=True,
                HTTP_HOST="desk.rexileer.ru",
            ).status_code,
            403,
        )
        csrf.get("/login/", secure=True, HTTP_HOST="desk.rexileer.ru")
        token = csrf.cookies[settings.CSRF_COOKIE_NAME].value
        response = csrf.post(
            "/login/",
            {
                "username": settings.OWNER_USERNAME,
                "password": "Synthetic-owner-password-123",
                "csrfmiddlewaretoken": token,
                "next": "https://attacker.invalid/stolen",
            },
            secure=True,
            HTTP_HOST="desk.rexileer.ru",
            HTTP_ORIGIN="https://desk.rexileer.ru",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
        self.assertEqual(
            csrf.get("/logout/", secure=True, HTTP_HOST="desk.rexileer.ru").status_code,
            405,
        )
        self.assertEqual(
            csrf.post(
                "/records/task/new/",
                {"title": "CSRF violation"},
                secure=True,
                HTTP_HOST="desk.rexileer.ru",
                HTTP_ORIGIN="https://attacker.invalid",
            ).status_code,
            403,
        )
        token = csrf.cookies[settings.CSRF_COOKIE_NAME].value
        response = csrf.post(
            "/logout/",
            {"csrfmiddlewaretoken": token},
            secure=True,
            HTTP_HOST="desk.rexileer.ru",
            HTTP_ORIGIN="https://desk.rexileer.ru",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            csrf.get(
                "/data/export/", secure=True, HTTP_HOST="desk.rexileer.ru"
            ).status_code,
            302,
        )

    def test_login_throttle_survives_new_clients_and_has_finite_lock(self):
        for index in range(8):
            client = Client()
            response = client.post(
                "/login/",
                {"username": "unknown-" + str(index), "password": "synthetic-invalid"},
                secure=True,
                HTTP_HOST="desk.rexileer.ru",
            )
            self.assertEqual(response.status_code, 200)
        response = self.client.post(
            "/login/",
            {
                "username": settings.OWNER_USERNAME,
                "password": "Synthetic-owner-password-123",
            },
            secure=True,
            HTTP_HOST="desk.rexileer.ru",
        )
        self.assertEqual(response.status_code, 429)
        self.assertEqual(LoginGuard.objects.get().attempts, 9)
        with patch(
            "desk.security.timezone.now",
            return_value=timezone.now() + timedelta(minutes=16),
        ):
            response = self.client.post(
                "/login/",
                {
                    "username": settings.OWNER_USERNAME,
                    "password": "Synthetic-owner-password-123",
                },
                secure=True,
                HTTP_HOST="desk.rexileer.ru",
            )
            self.assertEqual(response.status_code, 302)

    def test_health_is_loopback_only_and_contains_no_records(self):
        response = self.request("/health/")
        self.assertEqual(response.json(), {"ok": True})
        self.assertEqual(
            self.request("/health/", REMOTE_ADDR="198.18.0.1").status_code, 302
        )

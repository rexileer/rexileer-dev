from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import CreditContract


class DebtReviewTests(TestCase):
    route = "/credits/?scope=debt-review"

    def get(self, route=None):
        return self.client.get(
            route or self.route, secure=True, HTTP_HOST="desk.rexileer.tech"
        )

    def contract(self, title, folder, **review):
        return CreditContract.objects.create(
            title=title,
            kind="mfo",
            metadata={
                "debt_review_v1": {
                    "folder": folder,
                    "as_of": "2026-11-23",
                    **review,
                }
            },
        )

    def test_dated_totals_count_only_selected_current_review_values(self):
        self.contract(
            "Демо источник",
            1,
            balance="10.30",
            balance_kind="reported",
            daily_rate="0.8",
            daily_accrual="0",
            cap_pct=None,
            cap_note="Особое условие договора",
        )
        self.contract(
            "Демо расчёт",
            2,
            balance="2.70",
            balance_kind="estimated",
            balance_source="Источник от 15.11.2026, оценка на дату сверки",
        )
        self.contract(
            "Демо неизвестно",
            3,
            balance="999",
            balance_kind="unknown",
            daily_accrual=None,
        )
        self.contract(
            "Демо погашено",
            4,
            balance="0",
            balance_kind="reported",
            cap_pct="0",
            cap_amount="0",
            max_remaining="0",
        )
        self.contract(
            "Демо предыдущая сверка",
            5,
            balance="55",
            balance_kind="reported",
            as_of="2026-11-20",
        )
        self.contract("Демо неоднозначно", 6, balance="300", balance_kind="reported")
        self.contract("Демо дубль папки", 6, balance="400", balance_kind="estimated")
        self.contract(
            "Демо дата отсутствует",
            7,
            balance="100",
            balance_kind="reported",
            as_of=None,
        )
        CreditContract.objects.create(
            title="Договор без сверки", kind="mfo", borrowed=200
        )
        CreditContract.objects.create(
            title="Сверка не объект", kind="mfo", metadata={"debt_review_v1": 17}
        )
        self.assertRedirects(self.get(), "/login/", fetch_redirect_response=False)
        self.client.force_login(
            get_user_model().objects.create_user(
                settings.OWNER_USERNAME, is_superuser=True
            )
        )
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response["Cache-Control"])
        current, previous, undated = response.context["groups"]
        self.assertEqual(current["as_of"], date(2026, 11, 23))
        self.assertEqual(current["reported"], Decimal("10.30"))
        self.assertEqual(current["estimated"], Decimal("2.70"))
        self.assertEqual(current["total"], Decimal("13.00"))
        self.assertEqual(current["unknown"], 1)
        self.assertEqual(current["excluded"], 2)
        self.assertEqual(previous["total"], Decimal("55"))
        self.assertIsNone(undated["total"])
        self.assertContains(response, "0 ₽/сутки")
        self.assertContains(response, "0,8 %/день")
        self.assertContains(response, "0,00 ₽")
        self.assertContains(response, "Неизвестно")
        self.assertContains(response, "Особое условие договора")
        self.assertContains(response, "Источник от 15.11.2026")
        self.assertNotContains(response, "999,00")
        self.assertNotContains(response, "Договор без сверки")
        self.assertNotContains(response, "Сверка не объект")
        self.assertNotContains(response, "export.xlsx")
        self.assertContains(self.get("/credits/"), self.route)
        self.assertEqual(self.get("/credits/export.xlsx").status_code, 200)

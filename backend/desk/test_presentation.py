from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Change, Document, Obligation, Transaction
from .obligation_presentation import obligation_data, prepare_obligations
from .presentation import calendar_rows, today_context
from .services import save_record


class PresentationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            settings.OWNER_USERNAME, is_superuser=True
        )

    def save(self, entity, **fields):
        return save_record(entity, fields, actor="synthetic-test")[0]

    def get(self, path):
        self.client.force_login(self.user)
        response = self.client.get(path, secure=True, HTTP_HOST="desk.rexileer.ru")
        self.assertEqual(response.status_code, 200)
        return response

    def test_card_exposes_reported_amounts_schedule_and_actual_plan_without_writes(
        self,
    ):
        today = timezone.localdate()
        debt = self.save(
            "obligation",
            title="Synthetic creditor",
            metadata={
                "reference_amount_rub": "1234.56",
                "payoff_amount_reported_rub": "1500",
                "next_payment_date": (today - timedelta(days=10)).isoformat(),
                "schedule_text": "Каждые 14 дней · 2 из 6 со слов",
                "source_note_current": "Synthetic source <script>bad()</script>",
                "service_status_note": "Сайт недоступен; проверить",
                "addons_note": "Заявление требует проверки",
            },
        )
        plan = self.save(
            "payment",
            title="Synthetic next payment",
            obligation=debt.pk,
            due_date=today,
            amount="200",
            confirmed=True,
        )
        self.save("addon", title="Synthetic extra", obligation=debt.pk)
        before = Change.objects.count()
        response = self.get("/records/obligation/")
        for value in (
            "1 234,56 ₽",
            "1 500,00 ₽",
            "200,00 ₽",
            "Каждые 14 дней",
            "Допуслуги · 1",
            "Документы · 0",
            "План подтверждён",
        ):
            self.assertContains(response, value)
        self.assertNotContains(response, "<script>bad()")
        self.assertContains(response, "&lt;script&gt;")
        row = response.context["rows"][0]["obligation"]
        self.assertEqual(row["next_date"], today)
        self.assertEqual(row["next_url"], f"/records/payment/{plan.pk}/")
        self.assertEqual(Change.objects.count(), before)
        debt.refresh_from_db()
        self.assertIsNone(debt.balance)
        self.assertFalse(Transaction.objects.exists())

    def test_legacy_metadata_fallback_and_invalid_values_remain_source_only(self):
        day = timezone.localdate()
        debt = self.save(
            "obligation",
            title="Legacy synthetic",
            metadata={
                "source_record": {
                    "reference_amount_rub": "900.00",
                    "payoff_amount_reported_rub": "NaN",
                    "due": {
                        "date_candidate": day.isoformat(),
                        "date_year_inferred": True,
                    },
                    "installment": {
                        "amount_rub": "50",
                        "interval_days": 10,
                        "progress_text": "1 из 5",
                    },
                    "source_note": "Original synthetic source",
                }
            },
        )
        data = obligation_data(debt)
        self.assertEqual(data["next_date"], day)
        self.assertIn("Год", data["date_note"])
        self.assertIn("Каждые 10 дн.", data["schedule"])
        self.assertTrue(data["needs_check"])
        self.assertFalse(
            any(f["label"] == "Сообщено к возврату" for f in data["facts"])
        )
        debt.metadata = {
            "next_payment_date": "31.02",
            "reference_amount_rub": "Infinity",
            "source_record": {"due": {"date_candidate": day.isoformat()}},
        }
        data = obligation_data(debt)
        self.assertIsNone(data["next_date"])

    def test_nearest_sort_search_verification_and_reported_paid_filter(self):
        today = timezone.localdate()
        later = self.save(
            "obligation",
            title="A later",
            metadata={"next_payment_date": (today + timedelta(days=3)).isoformat()},
        )
        early = self.save(
            "obligation",
            title="Z early",
            metadata={
                "next_payment_date": today.isoformat(),
                "service_status_note": "Нужна проверка",
                "source_note_current": "Нужна сверка · synthetic note",
            },
        )
        self.save(
            "obligation",
            title="Confirmed no date",
            balance="12.00",
            balance_as_of=today,
        )
        paid = self.save(
            "obligation",
            title="Paid synthetic",
            archived=True,
            metadata={
                "lifecycle": "paid_reported",
                "next_payment_date": today.isoformat(),
            },
        )
        response = self.get("/records/obligation/")
        self.assertEqual(
            [r["record"].pk for r in response.context["rows"]][:2], [early.pk, later.pk]
        )
        self.assertNotContains(response, paid.title)
        self.assertContains(self.get("/records/obligation/?state=paid"), paid.title)
        self.assertContains(self.get("/records/obligation/?check=service"), early.title)
        response = self.get("/records/obligation/?q=НУЖНА&state=all&order=name")
        self.assertEqual(len(response.context["rows"]), 1)
        self.assertContains(response, early.title)
        response = self.get("/records/obligation/?check=has_balance")
        self.assertContains(response, "Confirmed no date")
        self.assertNotContains(response, early.title)

    def test_calendar_includes_unknown_amount_drafts_excludes_undated_archived_and_covered(
        self,
    ):
        today = timezone.localdate()
        debt = self.save("obligation", title="Synthetic calendar debt")
        draft = self.save(
            "payment", title="Dated no amount", obligation=debt.pk, due_date=today
        )
        self.save(
            "payment",
            title="Dated estimate",
            obligation=debt.pk,
            due_date=today,
            amount="700",
            metadata={"is_estimate": True},
        )
        self.save("payment", title="Undated", obligation=debt.pk)
        self.save(
            "payment",
            title="Archived",
            obligation=debt.pk,
            due_date=today,
            archived=True,
        )
        covered = self.save(
            "payment",
            title="Covered",
            obligation=debt.pk,
            due_date=today,
            amount="10",
            confirmed=True,
        )
        self.save(
            "transaction",
            title="Synthetic actual",
            direction="expense",
            amount="10",
            date=today,
            confirmed=True,
            payment=covered.pk,
        )
        rows = calendar_rows()
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["unverified"] for r in rows))
        self.assertEqual(
            next(r for r in rows if r["url"].endswith(f"/{draft.pk}/"))["detail"],
            "Уточнить сумму",
        )
        context = today_context()
        self.assertEqual(context["expense"], Decimal("10.00"))
        self.assertEqual(context["expected_total"], Decimal("0.00"))
        response = self.get("/calendar/")
        self.assertContains(response, "Из заметки · проверить")
        self.assertNotContains(response, "Просрочено")

    def test_indirect_documents_count_and_link_filter_match_without_decryption(self):
        debt = self.save("obligation", title="Synthetic files")
        other = self.save("obligation", title="Other synthetic")
        addon = self.save("addon", title="Synthetic addon", obligation=debt.pk)
        doc = Document.objects.create(
            title="Synthetic metadata only",
            kind="other",
            addon=addon,
            original_name="synthetic.pdf",
            content_type="application/pdf",
            size=10,
            sha256="a" * 64,
        )
        Document.objects.create(
            title="Other file",
            kind="other",
            obligation=other,
            original_name="other.pdf",
            content_type="application/pdf",
            size=10,
            sha256="b" * 64,
        )
        record = prepare_obligations(Obligation.objects.filter(pk=debt.pk)).get()
        self.assertEqual(obligation_data(record)["doc_count"], 1)
        response = self.get(f"/documents/?obligation={debt.pk}")
        self.assertContains(response, doc.title)
        self.assertNotContains(response, "Other file")

    def test_fully_paid_plan_does_not_resurface_as_metadata_deadline(self):
        today = timezone.localdate()
        debt = self.save(
            "obligation",
            title="Synthetic covered debt",
            metadata={"next_payment_date": today.isoformat()},
        )
        plan = self.save(
            "payment",
            title="Synthetic covered plan",
            obligation=debt.pk,
            due_date=today,
            amount="20",
            confirmed=True,
        )
        self.save(
            "transaction",
            title="Actual synthetic",
            direction="expense",
            amount="20",
            date=today,
            confirmed=True,
            payment=plan.pk,
        )
        self.assertIsNone(obligation_data(debt)["next_date"])

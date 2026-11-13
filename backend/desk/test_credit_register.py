import copy
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from tempfile import TemporaryDirectory

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from openpyxl import load_workbook

from .bureau_import import import_bureau
from .documents import decrypt_document, upload_document
from .models import (
    Change,
    CreditContract,
    CreditSnapshot,
    Document,
    Transaction,
)
from .presentation import today_context
from .services import save_record, snapshot


class CreditRegisterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user(
            settings.OWNER_USERNAME, is_superuser=True
        )

    def bundle(self, count=1):
        return {
            "version": 1,
            "batch": "synthetic-october",
            "records": [
                {
                    "uid": f"synthetic-contract-uid-{i:04d}",
                    "contract": {
                        "title": "Демо Банк" if i % 2 == 0 else "Демо МКК",
                        "kind": "bank" if i % 2 == 0 else "mfo",
                        "signed_on": "2026-09-01",
                        "product_kind": "Договор из синтетического источника",
                    },
                    "snapshot": {
                        "bureau": "NBKI",
                        "report_date": "2026-10-27",
                        "information_updated": "2026-10-14",
                        "reported_balance": "123.45",
                        "overdue_reported": "0.00",
                        "limit_amount": "900.00",
                        "metadata": {"pages": [12], "contract_date": "2026-09-01"},
                    },
                }
                for i in range(count)
            ],
        }

    def get(self, route):
        self.client.force_login(self.owner)
        return self.client.get(route, secure=True, HTTP_HOST="desk.rexileer.ru")

    def test_preview_idempotence_keeps_manual_ledger_and_does_not_infer_money(self):
        manual, _ = save_record(
            "obligation",
            {
                "title": "Synthetic manual",
                "metadata": {"next_payment_date": "2026-11-15"},
            },
            actor="test",
        )
        before = snapshot(manual)
        bundle = self.bundle()
        bundle["records"][0]["contract"].update(
            manual_obligation=manual.pk, link_status="unverified"
        )
        preview = import_bureau(bundle, actor="test")
        self.assertEqual(preview["created"], 1)
        self.assertFalse(CreditContract.objects.exists())
        import_bureau(bundle, actor="test", dry_run=False)
        second = import_bureau(bundle, actor="test", dry_run=False)
        self.assertEqual(second["changed"], 0)
        credit = CreditContract.objects.get()
        self.assertIsNone(credit.borrowed)
        self.assertIsNone(credit.paid_reported)
        self.assertIsNone(credit.next_due)
        self.assertEqual(credit.assignment_status, "unknown")
        self.assertEqual(credit.calls, "")
        manual.refresh_from_db()
        self.assertEqual(snapshot(manual), before)
        self.assertFalse(Transaction.objects.exists())
        self.assertEqual(today_context()["income"], Decimal("0.00"))
        self.assertEqual(today_context()["expense"], Decimal("0.00"))
        self.assertEqual(self.get("/credits/?scope=manual").status_code, 200)

    def test_reimport_does_not_overwrite_current_refinements_or_immutable_evidence(
        self,
    ):
        bundle = self.bundle()
        import_bureau(bundle, actor="test", dry_run=False)
        credit = CreditContract.objects.get()
        save_record(
            "credit",
            {
                "notes": "New manual fact",
                "paid_reported": "40.00",
                "next_due": "2026-11-20",
            },
            instance=credit,
            actor="owner",
        )
        self.assertEqual(
            import_bureau(bundle, actor="test", dry_run=False)["changed"], 0
        )
        credit.refresh_from_db()
        self.assertEqual(credit.notes, "New manual fact")
        self.assertEqual(credit.paid_reported, Decimal("40.00"))
        bad = copy.deepcopy(bundle)
        bad["records"][0]["snapshot"]["reported_balance"] = "100.00"
        with self.assertRaises(ValidationError):
            import_bureau(bad, actor="test", dry_run=False)
        self.assertEqual(
            CreditSnapshot.objects.get().reported_balance, Decimal("123.45")
        )

    def test_invalid_or_duplicate_package_rolls_back_every_record_and_history(self):
        bundle = self.bundle(2)
        bundle["records"][1]["snapshot"]["reported_balance"] = "-1.00"
        with self.assertRaises(ValidationError):
            import_bureau(bundle, actor="test", dry_run=False)
        self.assertEqual(CreditContract.objects.count(), 0)
        self.assertEqual(Change.objects.count(), 0)
        bundle = self.bundle()
        bundle["records"].append(copy.deepcopy(bundle["records"][0]))
        with self.assertRaises(ValidationError):
            import_bureau(bundle, actor="test", dry_run=False)
        self.assertFalse(CreditContract.objects.exists())

    def test_contract_uid_cannot_be_changed_and_assignment_requires_source(self):
        import_bureau(self.bundle(), actor="test", dry_run=False)
        credit = CreditContract.objects.get()
        with self.assertRaises(ValidationError):
            save_record("credit", {"uid": "another-uid"}, instance=credit, actor="test")
        with self.assertRaises(ValidationError):
            save_record(
                "credit",
                {"assignment_status": "documented", "assignee": "Synthetic entity"},
                instance=credit,
                actor="test",
            )
        self.assertEqual(
            self.get(
                f"/records/credit_snapshot/{CreditSnapshot.objects.get().pk}/"
            ).status_code,
            404,
        )

        manual, _ = save_record(
            "obligation", {"title": "Other synthetic manual"}, actor="test"
        )
        with self.assertRaises(ValidationError):
            Document(credit=credit, obligation=manual).clean()

    def test_filters_dates_unicode_and_full_xlsx_not_just_page(self):
        import_bureau(self.bundle(61), actor="test", dry_run=False)
        page = self.get("/credits/")
        self.assertEqual(len(page.context["rows"]), 50)
        response = self.get("/credits/export.xlsx?page=2")
        book = load_workbook(BytesIO(response.content))
        self.assertEqual(book.active.max_row, 62)
        self.assertEqual(book.active.freeze_panes, "B2")
        self.assertTrue(book.active.auto_filter.ref)
        filtered = self.get(
            "/credits/export.xlsx?kind=mfo&q=ДЕМО&from=2026-09-01&snapshot_to=2026-10-27"
        )
        book = load_workbook(BytesIO(filtered.content))
        self.assertEqual(book.active.max_row, 31)
        headings = {cell.value: cell.column for cell in book.active[1]}
        self.assertIsInstance(
            book.active.cell(2, headings["Дата оформления"]).value, datetime
        )
        self.assertIsNone(book.active.cell(2, headings["Выдано, ₽"]).value)
        self.assertEqual(
            self.get("/credits/?snapshot_from=2026-11-01").context["total"], 0
        )
        self.assertContains(page, "датированные источниковые снимки")

    def test_xlsx_formula_like_strings_are_literal_and_unknown_is_blank(self):
        bundle = self.bundle()
        bundle["records"][0]["contract"]["title"] = (
            '=HYPERLINK("https://invalid.test","demo")'
        )
        import_bureau(bundle, actor="test", dry_run=False)
        credit = CreditContract.objects.get()
        save_record(
            "credit",
            {"notes": "+SUM(1,2)", "call_notes": "@formula", "brand": "-1+2"},
            instance=credit,
            actor="owner",
        )
        response = self.get("/credits/export.xlsx")
        book = load_workbook(BytesIO(response.content), data_only=False)
        self.assertEqual(book.active["A2"].data_type, "s")
        self.assertFalse(
            any(
                cell.data_type == "f" or cell.hyperlink
                for row in book.active
                for cell in row
            )
        )
        self.assertIn("no-store", response["Cache-Control"])

    def test_export_edit_and_document_routes_are_private_on_every_host(self):
        for route in (
            "/credits/",
            "/credits/export.xlsx",
            "/records/credit/new/",
            "/documents/new/?credit=1",
        ):
            self.assertEqual(
                self.client.get(
                    route, secure=True, HTTP_HOST="desk.rexileer.ru"
                ).status_code,
                302,
            )
        self.client.force_login(self.owner)
        self.assertEqual(
            self.client.get(
                "/credits/export.xlsx", secure=True, HTTP_HOST="rexileer.ru"
            ).status_code,
            400,
        )
        self.assertEqual(
            self.client.get(
                "/credits/export.xlsx",
                secure=True,
                HTTP_HOST="desk.rexileer.ru",
                HTTP_ORIGIN="https://rexileer.ru",
            ).status_code,
            403,
        )

    def test_pdf_is_encrypted_and_bound_to_exact_uid_with_owner_checked_bytes(self):
        import_bureau(self.bundle(2), actor="test", dry_run=False)
        credit = CreditContract.objects.first()
        pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\n%%EOF\n"
        with (
            TemporaryDirectory() as directory,
            override_settings(DOCUMENT_ROOT=directory),
        ):
            doc = upload_document(
                {
                    "title": "Synthetic contract",
                    "kind": "agreement",
                    "credit": credit,
                },
                SimpleUploadedFile("synthetic.pdf", pdf, "application/pdf"),
                actor="test",
            )
            self.assertEqual(decrypt_document(doc), pdf)
            self.assertEqual(Document.objects.get().credit_id, credit.pk)
            response = self.get(f"/documents/?credit={credit.pk}")
            self.assertContains(response, "Synthetic contract")
            other = CreditContract.objects.exclude(pk=credit.pk).get()
            self.assertNotContains(
                self.get(f"/documents/?credit={other.pk}"), "Synthetic contract"
            )
            self.assertEqual(self.get(f"/documents/{doc.pk}/download/").content, pdf)
            self.client.logout()
            self.assertEqual(
                self.client.get(
                    f"/documents/{doc.pk}/download/",
                    secure=True,
                    HTTP_HOST="desk.rexileer.ru",
                ).status_code,
                302,
            )

    def test_same_brand_multiple_uids_and_two_legal_entities_are_not_collapsed(self):
        bundle = self.bundle(3)
        for row in bundle["records"]:
            row["contract"]["title"] = "Synthetic legal A"
        bundle["records"][2]["contract"]["title"] = "Synthetic legal B"
        import_bureau(bundle, actor="test", dry_run=False)
        self.assertEqual(CreditContract.objects.count(), 3)
        self.assertEqual(CreditSnapshot.objects.count(), 3)
        self.assertContains(self.get("/credits/"), "Synthetic legal B")

    def test_explicit_dated_financing_and_paid_facts_are_visible_without_cash_or_inference(
        self,
    ):
        bundle = self.bundle()
        bundle["records"][0]["snapshot"]["metadata"]["verified_financial_facts"] = {
            "verification": "checked_source",
            "source_label": "Synthetic bureau",
            "as_of": "2026-10-15",
            "issued": "2000.00",
            "paid_total": "500.00",
            "next_date": "2026-11-21",
            "next_principal": "100.00",
            "next_interest": "20.00",
            "interest_balance": "30.00",
            "limit": "9000.00",
        }
        import_bureau(bundle, actor="test", dry_run=False)
        response = self.get("/credits/")
        row = response.context["rows"][0]
        self.assertEqual(row["borrowed"], Decimal("2000.00"))
        self.assertEqual(row["paid"], Decimal("500.00"))
        self.assertEqual(row["next_amount"], Decimal("120.00"))
        self.assertIn("15.10.2026", row["paid_source"])
        credit = CreditContract.objects.get()
        self.assertIsNone(credit.borrowed)
        self.assertIsNone(credit.paid_reported)
        self.assertFalse(Transaction.objects.exists())
        self.assertEqual(today_context()["expense"], Decimal("0.00"))
        self.assertContains(
            self.get(f"/records/credit/{credit.pk}/"), "Первоначальное финансирование"
        )
        save_record(
            "credit",
            {"paid_reported": "700.00", "next_amount": "200.00"},
            instance=credit,
            actor="owner",
        )
        row = self.get("/credits/").context["rows"][0]
        self.assertEqual(row["paid"], Decimal("700.00"))
        self.assertEqual(row["paid_source"], "")
        self.assertIsNone(row["next_due"])

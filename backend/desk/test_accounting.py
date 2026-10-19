from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Change, ExpectedIncome, Project, Task, Transaction
from .presentation import calendar_rows, today_context
from .services import (
    current_balance,
    import_records,
    paid_amount,
    read_records,
    remaining,
    save_record,
)


class AccountingTests(TestCase):
    def save(self, kind, **fields):
        return save_record(kind, fields, actor="synthetic-test")[0]

    def expense(self, **values):
        return self.save(
            "transaction",
            title="Synthetic transfer",
            direction="expense",
            amount="125.25",
            date=timezone.localdate(),
            confirmed=True,
            **values,
        )

    def test_principal_only_after_confirmed_snapshot_and_unknown_is_not_zero(self):
        today = timezone.localdate()
        debt = self.save(
            "obligation",
            title="Synthetic obligation",
            balance="1000.00",
            balance_as_of=today - timedelta(days=1),
        )
        self.save(
            "payment",
            title="Synthetic plan",
            obligation=debt.pk,
            amount="500.00",
            due_date=today,
            confirmed=True,
        )
        self.assertEqual(current_balance(debt), Decimal("1000.00"))
        payment = self.expense(obligation=debt.pk, principal="100.25")
        self.assertEqual(current_balance(debt), Decimal("899.75"))
        save_record("transaction", {"archived": True}, actor="test", instance=payment)
        self.assertEqual(current_balance(debt), Decimal("1000.00"))
        unknown = self.save("obligation", title="Unknown balance")
        self.expense(obligation=unknown.pk, principal="10.00")
        self.assertIsNone(current_balance(unknown))
        same_day = self.save(
            "obligation",
            title="Snapshot same day",
            balance="500.00",
            balance_as_of=today,
        )
        self.expense(obligation=same_day.pk, principal="100.00")
        self.assertEqual(current_balance(same_day), Decimal("500.00"))

    def test_partial_payment_state_comes_only_from_real_operations(self):
        debt = self.save("obligation", title="Unknown balance")
        plan = self.save(
            "payment",
            title="Synthetic plan",
            obligation=debt.pk,
            amount="300.50",
            due_date=timezone.localdate(),
            confirmed=True,
        )
        self.assertEqual(remaining(plan), Decimal("300.50"))
        self.expense(payment=plan.pk)
        self.assertEqual(paid_amount(plan), Decimal("125.25"))
        self.assertEqual(remaining(plan), Decimal("175.25"))
        self.assertIsNone(current_balance(debt))

    def test_expected_and_actual_do_not_double_count_and_tracks_remain_separate(self):
        expected = self.save(
            "expected",
            title="Synthetic new work",
            amount="500.00",
            due_date=timezone.localdate(),
            track="new",
        )
        self.save(
            "transaction",
            title="Synthetic partial receipt",
            direction="income",
            amount="120.50",
            date=timezone.localdate(),
            confirmed=True,
            expected=expected.pk,
        )
        self.save(
            "expected",
            title="Unconfirmed proposal",
            amount="999.00",
            due_date=timezone.localdate(),
            status="proposal",
        )
        self.assertEqual(remaining(expected), Decimal("379.50"))
        summary = today_context()
        self.assertEqual(summary["income"], Decimal("120.50"))
        self.assertEqual(summary["expected_total"], Decimal("379.50"))
        self.assertEqual(Transaction.objects.get().track, "new")

    def test_invalid_money_dates_and_links_are_atomic(self):
        for bad in ["-1.00", "0.00", "1.001", "NaN", True, 1.25]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                self.save(
                    "transaction",
                    title="Invalid",
                    direction="income",
                    amount=bad,
                    date=timezone.localdate(),
                    confirmed=True,
                )
        for fields in [
            {"confirmed": False},
            {"date": timezone.localdate() + timedelta(days=1)},
            {"principal": "126.00"},
        ]:
            values = {
                "title": "Invalid",
                "direction": "expense",
                "amount": "125.00",
                "date": timezone.localdate(),
                "confirmed": True,
                **fields,
            }
            with self.assertRaises(ValidationError):
                self.save("transaction", **values)
        self.assertFalse(Transaction.objects.exists())
        self.assertFalse(Change.objects.exists())

    def test_over_repayment_and_mismatched_obligation_are_rejected(self):
        debt = self.save(
            "obligation",
            title="Synthetic",
            balance="20.00",
            balance_as_of=timezone.localdate() - timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            self.expense(obligation=debt.pk, principal="25.00")
        plan = self.save(
            "payment",
            title="Plan",
            obligation=debt.pk,
            amount="10.00",
            confirmed=True,
            due_date=timezone.localdate(),
        )
        other = self.save("obligation", title="Other")
        with self.assertRaises(ValidationError):
            self.expense(payment=plan.pk, obligation=other.pk)
        self.assertFalse(Transaction.objects.exists())

    def test_draft_and_unknown_dates_do_not_become_overdue(self):
        debt = self.save(
            "obligation",
            title="Unverified amount",
            metadata={"reference_amount": "900.00", "incomplete": True},
        )
        self.save("payment", title="Unknown date", obligation=debt.pk)
        self.save(
            "payment",
            title="Unverified old date",
            obligation=debt.pk,
            amount="100.00",
            due_date=timezone.localdate() - timedelta(days=100),
        )
        self.assertEqual(calendar_rows(), [])
        self.assertIsNone(current_balance(debt))
        self.save("task", title="Complete task", status="done")
        self.assertFalse(Transaction.objects.exists())

    def test_import_preview_idempotence_references_and_full_rollback(self):
        rows = [
            {
                "entity": "task",
                "source": "synthetic",
                "external_id": "t1",
                "fields": {
                    "title": "Synthetic task",
                    "project": {"source": "synthetic", "external_id": "p1"},
                },
            },
            {
                "entity": "project",
                "source": "synthetic",
                "external_id": "p1",
                "fields": {
                    "name": "Synthetic project",
                    "metadata": {"historical_paid": "1000.00"},
                },
            },
        ]
        import_records(rows, actor="test", dry_run=True)
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(Change.objects.count(), 0)
        import_records(rows, actor="test", dry_run=False)
        second = import_records(rows, actor="test", dry_run=False)
        self.assertFalse(any(row["changed"] for row in second))
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Change.objects.count(), 2)
        self.assertFalse(Transaction.objects.exists())
        invalid = rows + [
            {
                "entity": "expected",
                "source": "synthetic",
                "external_id": "bad",
                "fields": {"title": "Bad", "amount": "-1.00"},
            }
        ]
        with self.assertRaises(ValidationError):
            import_records(invalid, actor="test", dry_run=False)
        self.assertEqual(ExpectedIncome.objects.count(), 0)
        with self.assertRaises(ValidationError):
            import_records(rows + rows[:1], actor="test", dry_run=False)

    def test_csv_and_backup_json_preserve_decimal_values(self):
        rows = read_records(
            b"entity,source,external_id,title,amount\nexpected,synthetic,x,Synthetic,123.45\n",
            "csv",
        )
        import_records(rows, actor="test", dry_run=False)
        self.assertEqual(ExpectedIncome.objects.get().amount, Decimal("123.45"))
        with self.assertRaises(ValidationError):
            self.save("obligation", title="No snapshot date", balance="10.00")

    def test_addon_status_does_not_create_cash_or_a_false_refund(self):
        self.save(
            "addon",
            title="Synthetic service",
            reported_amount="20.00",
            status="refund_expected",
        )
        self.assertFalse(Transaction.objects.exists())
        self.assertEqual(today_context()["expected_total"], Decimal("0.00"))
        with self.assertRaises(ValidationError):
            self.save("addon", title="Invalid refund", status="received")

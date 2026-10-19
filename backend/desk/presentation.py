from datetime import date, timedelta

from django.utils import timezone

from .models import ZERO, ExpectedIncome, PlannedPayment, Task, Transaction
from .services import remaining, total


def money(value):
    if value is None:
        return "Неизвестно"
    return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " ₽"


def href(entity, record):
    return f"/records/{entity}/{record.pk}/"


def calendar_rows(days=30):
    today = timezone.localdate()
    end = today + timedelta(days=days - 1)
    rows = []
    for task in Task.objects.filter(archived=False, due_date__lte=end).exclude(
        status="done"
    ):
        rows.append(
            {
                "date": task.due_date,
                "title": task.title,
                "kind": "Задача",
                "detail": task.get_status_display(),
                "url": href("task", task),
            }
        )
    for payment in PlannedPayment.objects.filter(
        archived=False, confirmed=True, due_date__lte=end
    ):
        left = remaining(payment)
        if left > ZERO:
            rows.append(
                {
                    "date": payment.due_date,
                    "title": payment.title,
                    "kind": "Плановый расход",
                    "detail": money(left) + " осталось",
                    "url": href("payment", payment),
                }
            )
    for expected in ExpectedIncome.objects.filter(
        archived=False, status="expected", due_date__lte=end
    ):
        left = remaining(expected)
        if left > ZERO:
            rows.append(
                {
                    "date": expected.due_date,
                    "title": expected.title,
                    "kind": "Ожидаемый приход",
                    "detail": money(left) + " — ещё не получено",
                    "url": href("expected", expected),
                }
            )
    for row in rows:
        row["overdue"] = row["date"] < today
    return sorted(rows, key=lambda row: (row["date"], row["kind"], row["title"]))


def today_context(window=7):
    today = timezone.localdate()
    start = today - timedelta(days=window - 1)
    operations = list(
        Transaction.objects.filter(
            archived=False, confirmed=True, date__range=(start, today)
        )
    )
    income = total(t.amount for t in operations if t.direction == "income")
    expense = total(t.amount for t in operations if t.direction == "expense")
    expected = [
        e
        for e in ExpectedIncome.objects.filter(
            archived=False,
            status="expected",
            due_date__lte=today + timedelta(days=window - 1),
        )
        if remaining(e) > ZERO
    ]
    tasks = list(Task.objects.filter(archived=False).exclude(status="done"))
    tasks.sort(
        key=lambda t: (
            not (t.due_date and t.due_date < today),
            t.priority,
            t.due_date or date.max,
            t.created_at,
        )
    )
    actions = []
    for task in tasks[:8]:
        explanation = task.get_priority_display() + " важность"
        if task.due_date:
            delta = (task.due_date - today).days
            explanation += "; " + (
                f"просрочено на {-delta} дн."
                if delta < 0
                else "срок сегодня"
                if delta == 0
                else f"срок через {delta} дн."
            )
        else:
            explanation += "; без срока"
        actions.append(
            {"record": task, "url": href("task", task), "explanation": explanation}
        )
    days = []
    for index in range(window):
        day = start + timedelta(days=index)
        inc = total(
            t.amount for t in operations if t.direction == "income" and t.date == day
        )
        out = total(
            t.amount for t in operations if t.direction == "expense" and t.date == day
        )
        days.append(
            {
                "date": day,
                "income": inc,
                "expense": out,
                "x": index * 24 + 3,
                "x2": index * 24 + 12,
            }
        )
    maximum = max(
        [int(row[key] * 100) for row in days for key in ("income", "expense")] + [1]
    )
    for row in days:
        for key in ("income", "expense"):
            height = int(row[key] * 100) * 88 // maximum
            row[key + "_height"] = height
            row[key + "_y"] = 100 - height
    return {
        "today": today,
        "window": window,
        "actions": actions,
        "calendar": calendar_rows(window)[:12],
        "income": income,
        "expense": expense,
        "net": income - expense,
        "expected_total": total(remaining(e) for e in expected),
        "days": days,
        "chart_width": window * 24,
        "has_operations": bool(operations),
    }

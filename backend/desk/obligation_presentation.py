"""Read-only source summaries. Reported figures never become ledger balances."""

from datetime import date
from decimal import Decimal, InvalidOperation

from django.db.models import Count, IntegerField, OuterRef, Prefetch, Q, Subquery, Value
from django.db.models.functions import Coalesce

from .models import Addon, Document, PlannedPayment
from .presentation import href, money
from .services import current_balance, remaining


def mapping(value):
    return value if isinstance(value, dict) else {}


def text(value):
    return str(value).strip() if isinstance(value, (str, int, float, Decimal)) else ""


def reported_money(value):
    try:
        amount = Decimal(
            text(value).replace(" ", "").replace("\u00a0", "").replace(",", ".")
        )
        if amount.is_finite() and 0 <= amount <= Decimal("9999999999.99"):
            return money(amount)
    except InvalidOperation:
        pass
    return ""


def source_date(value):
    try:
        return date.fromisoformat(text(value))
    except ValueError:
        return None


def document_obligation_filter(value):
    return (
        Q(obligation_id=value)
        | Q(payment__obligation_id=value)
        | Q(addon__obligation_id=value)
        | Q(letter__obligation_id=value)
        | Q(email__obligation_id=value)
        | Q(transaction__obligation_id=value)
    )


def prepare_obligations(query):
    docs = (
        Document.objects.filter(
            document_obligation_filter(OuterRef("pk")), archived=False
        )
        .order_by()
        .annotate(group=Value(1))
        .values("group")
        .annotate(count=Count("pk", distinct=True))
        .values("count")
    )
    return query.annotate(
        desk_doc_count=Coalesce(Subquery(docs, output_field=IntegerField()), 0),
        desk_addon_count=Count("addon", filter=Q(addon__archived=False), distinct=True),
    ).prefetch_related(
        Prefetch(
            "plannedpayment_set",
            queryset=PlannedPayment.objects.filter(archived=False).order_by(
                "due_date", "pk"
            ),
            to_attr="desk_plans",
        )
    )


def obligation_data(record):
    meta = mapping(record.metadata)
    source = mapping(meta.get("source_record"))
    due = mapping(source.get("due"))
    installment = mapping(source.get("installment"))
    lifecycle = text(meta.get("lifecycle") or source.get("status"))
    paid_reported = lifecycle in ("paid_reported", "closed_reported")
    plans = getattr(record, "desk_plans", None)
    if plans is None:
        plans = list(
            record.plannedpayment_set.filter(archived=False).order_by("due_date", "pk")
        )
    dated = [p for p in plans if p.due_date]
    open_plans = [p for p in dated if p.amount is None or remaining(p) > 0]
    next_plan = min(open_plans, key=lambda p: (p.due_date, p.pk), default=None)
    next_date = next_plan.due_date if next_plan else None
    # A paid or fully covered plan must not reappear from stale source metadata.
    if not dated and not paid_reported and not record.archived:
        next_date = source_date(meta.get("next_payment_date"))
        if "next_payment_date" not in meta and not due.get("superseded_possible"):
            next_date = source_date(due.get("date_candidate"))
    if paid_reported or record.archived:
        next_plan, next_date = None, None
    next_amount = (
        money(remaining(next_plan))
        if next_plan and next_plan.amount is not None
        else reported_money(
            meta.get("next_payment_amount_rub", installment.get("amount_rub"))
        )
    )
    confirmed = bool(next_plan and next_plan.confirmed)
    facts = []
    reference = reported_money(
        meta.get("reference_amount_rub", source.get("reference_amount_rub"))
    )
    payoff = reported_money(
        meta.get("payoff_amount_reported_rub", source.get("payoff_amount_reported_rub"))
    )
    if reference:
        facts.append(
            {
                "label": "Сумма из заметки",
                "value": reference,
                "hint": "Не подтверждённый остаток",
            }
        )
    if payoff:
        facts.append(
            {
                "label": "Сообщено к возврату",
                "value": payoff,
                "hint": "Из заметки · проверить",
            }
        )
    if not paid_reported and not record.archived:
        facts.append(
            {
                "label": "Ближайший платёж" if confirmed else "Платёж из заметки",
                "value": next_amount or "Сумма не указана",
                "hint": "План подтверждён"
                if confirmed
                else "Сумму уточнить · не подтверждено",
            }
        )
    balance = current_balance(record)
    facts.append(
        {
            "label": "Подтверждённый остаток"
            if balance is None
            else "Остаток по учёту",
            "value": money(balance) if balance is not None else "Не указан",
            "hint": "Нужны сумма и дата"
            if balance is None
            else "Снимок на "
            + record.balance_as_of.strftime("%d.%m.%Y")
            + " · без начислений",
        }
    )
    schedule = text(meta.get("schedule_text"))
    if not schedule:
        parts = []
        for key, unit in (("interval_days", "дн."), ("interval_months", "мес.")):
            interval = installment.get(key)
            if isinstance(interval, int) and interval > 0:
                parts.append(f"Каждые {interval} {unit}")
        if text(installment.get("progress_text")):
            parts.append(text(installment["progress_text"]))
        schedule = " · ".join(parts)
    note = text(
        meta.get("source_note_current") or source.get("source_note") or record.notes
    )
    payment_note = text(meta.get("payment_status_note"))
    if not payment_note and (
        meta.get("reported_payment") or source.get("reported_payment")
    ):
        payment_note = "Есть сообщение об оплате; зачисление нужно проверить."
    service_note = text(meta.get("service_status_note"))
    addons_note = text(
        meta.get("addons_note") or source.get("extras_note") or source.get("fees_note")
    )
    addon_count = getattr(record, "desk_addon_count", None)
    if addon_count is None:
        addon_count = Addon.objects.filter(obligation=record, archived=False).count()
    doc_count = getattr(record, "desk_doc_count", None)
    if doc_count is None:
        doc_count = (
            Document.objects.filter(
                document_obligation_filter(record.pk), archived=False
            )
            .distinct()
            .count()
        )
    date_status = text(meta.get("date_status"))
    date_note = ""
    if date_status == "derived_from_reported_schedule":
        date_note = "Дата по графику; зачисление прошлого платежа проверить"
    elif (
        not confirmed
        and due.get("date_year_inferred")
        and "next_payment_date" not in meta
    ):
        date_note = "Год даты требует проверки"
    return {
        "facts": facts,
        "next_date": next_date,
        "next_url": href("payment", next_plan) if next_plan else "",
        "date_label": "Дата плана" if confirmed else "Дата из заметки · проверить",
        "date_note": date_note,
        "schedule": schedule,
        "note": note,
        "payment_note": payment_note,
        "service_note": service_note,
        "addons_note": addons_note,
        "addon_count": addon_count,
        "doc_count": doc_count,
        "paid_reported": paid_reported,
        "needs_check": balance is None
        or lifecycle == "needs_check"
        or bool(service_note)
        or (next_date is not None and not confirmed),
        "has_balance": balance is not None,
        "status": "Погашено со слов владельца"
        if paid_reported
        else "В архиве"
        if record.archived
        else "Нужна проверка сервиса"
        if service_note
        else "Действующее",
    }

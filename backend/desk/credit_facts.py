"""Explicit dated source facts only; never derive paid money from balances."""

from datetime import date
from decimal import Decimal, InvalidOperation


def source_facts(snapshot):
    if snapshot is None:
        return {}
    raw = snapshot.metadata.get("verified_financial_facts", {})
    if not isinstance(raw, dict) or raw.get("verification") != "checked_source":
        return {}
    facts = {"source_label": str(raw.get("source_label", "Источник"))[:100]}
    for key in (
        "issued",
        "paid_total",
        "next_principal",
        "next_interest",
        "interest_balance",
        "other_balance",
        "limit",
        "last_payment",
        "remaining_all_payments",
    ):
        try:
            value = Decimal(str(raw.get(key)))
            facts[key] = (
                value
                if value.is_finite() and 0 <= value <= Decimal("999999999999.99")
                else None
            )
        except InvalidOperation:
            facts[key] = None
    for key in ("as_of", "next_date", "last_payment_date"):
        try:
            facts[key] = date.fromisoformat(str(raw.get(key)))
        except ValueError:
            facts[key] = None
    facts["next_total"] = (
        facts["next_principal"] + facts["next_interest"]
        if facts["next_principal"] is not None and facts["next_interest"] is not None
        else None
    )
    facts["label"] = facts["source_label"] + (
        f" · {facts['as_of']:%d.%m.%Y}" if facts["as_of"] else " · дата не указана"
    )
    return facts

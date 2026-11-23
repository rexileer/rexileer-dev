"""Read the owner's selected loan review without inferring values from bureau data."""

import re
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal

from django.shortcuts import render

from .models import CreditContract

AMOUNTS = (
    "balance",
    "daily_rate",
    "daily_accrual",
    "cap_pct",
    "cap_amount",
    "max_remaining",
)
TEXTS = ("balance_source", "rate_label", "cap_note", "note")


def nonnegative_decimal(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{1,16}(\.[0-9]{1,8})?", value
    ):
        return None
    return Decimal(value)


def review_date(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value
    ):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def review_rows():
    rows = []
    contracts = CreditContract.objects.filter(
        metadata__has_key="debt_review_v1"
    ).order_by("title", "pk")
    for contract in contracts:
        data = contract.metadata.get("debt_review_v1")
        if not isinstance(data, dict):
            continue
        folder = data.get("folder")
        kind = data.get("balance_kind")
        rows.append(
            {
                "contract": contract,
                "folder": folder if type(folder) is int else None,
                "as_of": review_date(data.get("as_of")),
                "balance_kind": kind
                if kind in ("reported", "estimated")
                else "unknown",
                **{key: nonnegative_decimal(data.get(key)) for key in AMOUNTS},
                **{
                    key: data[key].strip() if isinstance(data.get(key), str) else ""
                    for key in TEXTS
                },
            }
        )
    return rows


def review(request):
    rows = review_rows()
    folders = Counter(row["folder"] for row in rows)
    by_date = defaultdict(list)
    for row in rows:
        row["folder_conflict"] = (
            row["folder"] is not None and folders[row["folder"]] > 1
        )
        if row["balance_kind"] == "unknown":
            row["balance"] = None
        by_date[row["as_of"]].append(row)

    groups = []
    for as_of in sorted(by_date, key=lambda day: day or date.min, reverse=True):
        dated_rows = by_date[as_of]
        balances = {"reported": [], "estimated": []}
        for row in dated_rows:
            if as_of and not row["folder_conflict"] and row["balance"] is not None:
                balances[row["balance_kind"]].append(row["balance"])
        known = balances["reported"] + balances["estimated"]
        groups.append(
            {
                "as_of": as_of,
                "rows": dated_rows,
                "total": sum(known) if known else None,
                "reported": sum(balances["reported"]) if balances["reported"] else None,
                "estimated": sum(balances["estimated"])
                if balances["estimated"]
                else None,
                "unknown": sum(row["balance"] is None for row in dated_rows),
                "excluded": sum(row["balance"] is not None for row in dated_rows)
                - len(known),
            }
        )
    return render(
        request,
        "desk/debt_review.html",
        {"title": "Текущие долги МФО", "groups": groups},
    )

"""Owner-only register and filtered XLSX; source snapshots are not cash balances."""

from datetime import date
from io import BytesIO

from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from .credit_facts import source_facts
from .models import CreditContract, CreditSnapshot, Obligation
from .obligation_presentation import obligation_data, prepare_obligations


def query_rows(request):
    scope = "manual" if request.GET.get("scope") == "manual" else "contracts"
    rows = []
    if scope == "manual":
        for obj in prepare_obligations(Obligation.objects.all()):
            info = obligation_data(obj)
            meta = obj.metadata
            rows.append(
                {
                    "record": obj,
                    "id": obj.pk,
                    "title": obj.title,
                    "url": f"/records/obligation/{obj.pk}/",
                    "kind": "family"
                    if meta.get("creditor_kind") == "family"
                    or meta.get("group_tag") == "family"
                    or obj.source == "owner_debts"
                    and obj.external_id.endswith(":parents")
                    else "unknown",
                    "kind_label": "Ручная запись",
                    "next_due": info["next_date"],
                    "note": info["note"],
                    "schedule": info["schedule"],
                    "archived": obj.archived,
                    "status": "closed" if info["paid_reported"] else "unknown",
                    "status_label": info["status"],
                    "source_note": "Сумма из заметки показана в карточке; не подтверждённый остаток",
                    "documents": info["doc_count"],
                    "upload": f"/documents/new/?obligation={obj.pk}",
                    "documents_url": f"/documents/?obligation={obj.pk}",
                    "search": obj.title + " " + obj.notes,
                    "manual": True,
                }
            )
    else:
        query = CreditContract.objects.select_related(
            "manual_obligation"
        ).prefetch_related(
            Prefetch(
                "snapshots",
                queryset=CreditSnapshot.objects.filter(archived=False).order_by(
                    "-report_date", "-pk"
                ),
                to_attr="source_snapshots",
            ),
            "document_set",
        )
        for obj in query:
            source = obj.source_snapshots[0] if obj.source_snapshots else None
            facts = source_facts(source)
            source_next = obj.next_due is None and obj.next_amount is None
            documents = [d for d in obj.document_set.all() if not d.archived]
            rows.append(
                {
                    "record": obj,
                    "id": obj.pk,
                    "title": obj.title,
                    "brand": obj.brand,
                    "kind": obj.kind,
                    "kind_label": obj.get_kind_display(),
                    "product_kind": obj.product_kind,
                    "contract_number": obj.contract_number,
                    "uid": obj.uid,
                    "signed_on": obj.signed_on,
                    "borrowed": obj.borrowed
                    if obj.borrowed is not None
                    else facts.get("issued"),
                    "paid": obj.paid_reported
                    if obj.paid_reported is not None
                    else facts.get("paid_total"),
                    "borrowed_source": facts.get("label", "")
                    if obj.borrowed is None and facts.get("issued") is not None
                    else "",
                    "paid_source": facts.get("label", "")
                    if obj.paid_reported is None and facts.get("paid_total") is not None
                    else "",
                    "next_due": facts.get("next_date") if source_next else obj.next_due,
                    "next_amount": facts.get("next_total")
                    if source_next
                    else obj.next_amount,
                    "next_source": facts.get("label", "")
                    if source_next and facts.get("next_date")
                    else "",
                    "interest_balance_source": facts.get("interest_balance"),
                    "financial_source_label": facts.get("label", ""),
                    "schedule": obj.schedule,
                    "rate": obj.rate,
                    "interest_accrued": obj.interest_accrued,
                    "interest_overdue": obj.interest_overdue,
                    "assignee": obj.assignee,
                    "representative": obj.representative,
                    "original_creditor": obj.original_creditor,
                    "assignment": obj.get_assignment_status_display(),
                    "calls": obj.get_calls_display() if obj.calls else "",
                    "call_notes": obj.call_notes,
                    "note": obj.notes,
                    "archived": obj.archived,
                    "status": obj.status,
                    "status_label": obj.get_status_display(),
                    "source": source,
                    "report_date": source.report_date if source else None,
                    "updated": source.information_updated if source else None,
                    "reported_balance": source.reported_balance if source else None,
                    "limit": source.limit_amount if source else None,
                    "principal_not_due": source.principal_not_due if source else None,
                    "bureau": source.bureau if source else "",
                    "overdue": source.overdue_reported if source else None,
                    "source_note": source.notes if source else "",
                    "financial_facts": facts,
                    "url": f"/records/credit/{obj.pk}/",
                    "documents": len(documents),
                    "upload": f"/documents/new/?credit={obj.pk}",
                    "documents_url": f"/documents/?credit={obj.pk}",
                    "manual_link": obj.manual_obligation,
                    "link_status": obj.get_link_status_display(),
                    "search": " ".join(
                        [
                            obj.title,
                            obj.brand,
                            obj.uid or "",
                            obj.contract_number,
                            obj.notes,
                            obj.original_creditor,
                            obj.assignee,
                            obj.representative,
                            obj.call_notes,
                        ]
                    ),
                }
            )
    for row in rows:
        for key in (
            "borrowed",
            "paid",
            "next_amount",
            "reported_balance",
            "limit",
            "overdue",
            "interest_accrued",
            "interest_overdue",
        ):
            row.setdefault(key, None)
    creditor_options = sorted({r["title"] for r in rows})
    needle = request.GET.get("q", "")[:160].casefold().strip()
    if needle:
        rows = [r for r in rows if needle in r["search"].casefold()]
    for field in ("kind", "status"):
        if request.GET.get(field):
            rows = [r for r in rows if r.get(field) == request.GET[field]]
    if request.GET.get("creditor"):
        rows = [r for r in rows if r["title"] == request.GET["creditor"]]
    activity = request.GET.get("activity", "visible")
    if activity != "all":
        rows = [r for r in rows if r["archived"] == (activity == "archived")]
    for param, field, lower in (
        ("from", "signed_on", True),
        ("to", "signed_on", False),
        ("snapshot_from", "report_date", True),
        ("snapshot_to", "report_date", False),
    ):
        if request.GET.get(param):
            try:
                limit = date.fromisoformat(request.GET[param])
                rows = [
                    r
                    for r in rows
                    if r.get(field)
                    and (r[field] >= limit if lower else r[field] <= limit)
                ]
            except ValueError:
                rows = []
    if request.GET.get("link") == "unlinked":
        rows = [r for r in rows if not r.get("manual_link")]
    elif request.GET.get("link") == "linked":
        rows = [r for r in rows if r.get("manual_link")]
    order = request.GET.get("order", "creditor")
    if order in ("signed_on", "next_due", "updated"):
        rows.sort(
            key=lambda r: (r.get(order) or date.max, r["title"].casefold(), r["id"])
        )
    else:
        rows.sort(
            key=lambda r: (
                r["title"].casefold(),
                r.get("signed_on") or date.max,
                r["id"],
            )
        )
    return scope, rows, creditor_options


def register(request):
    scope, rows, creditors = query_rows(request)
    objects = Paginator(rows, 50).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    complete, incomplete = [], []
    for row in rows:
        if row.get("uid") and row.get("signed_on") and row.get("source"):
            complete.append(
                f"{row['title']}, {row.get('product_kind') or 'вид договора не уточнён'}, {row['signed_on']:%m.%Y}"
            )
        else:
            incomplete.append(
                row["title"] + ": дата / UID / источник требуют уточнения"
            )
    response = render(
        request,
        "desk/credits.html",
        {
            "title": "Договоры и БКИ",
            "scope": scope,
            "rows": objects,
            "objects": objects,
            "kinds": CreditContract.KINDS,
            "creditors": creditors,
            "query_params": params.urlencode(),
            "copy_text": "По датированным источникам БКИ; актуальность обязательств требует проверки.\n"
            + "\n".join(complete),
            "incomplete_text": "\n".join(incomplete),
            "total": len(rows),
            "report_dates": ", ".join(
                day.strftime("%d.%m.%Y")
                for day in sorted(
                    {r["report_date"] for r in rows if r.get("report_date")}
                )
            ),
        },
    )
    response["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    return response


EXPORT_COLUMNS = [
    ("Кредитор в источнике", "title"),
    ("Бренд", "brand"),
    ("Тип", "kind_label"),
    ("Вид договора в источнике", "product_kind"),
    ("Номер договора, если известен", "contract_number"),
    ("УИД (не номер договора)", "uid"),
    ("Дата оформления", "signed_on"),
    ("Выдано, ₽", "borrowed"),
    ("Источник выданной суммы", "borrowed_source"),
    ("Погашено по источнику, ₽", "paid"),
    ("Источник погашения", "paid_source"),
    ("Ближайший срок (ручной / источник)", "next_due"),
    ("Взнос, ₽ (ручной / источник)", "next_amount"),
    ("Источник даты и взноса, если не ручной", "next_source"),
    ("График", "schedule"),
    ("Ставка и период", "rate"),
    ("Начисленные проценты, ₽", "interest_accrued"),
    ("Просроченные проценты, ₽", "interest_overdue"),
    ("Проценты в остатке по источнику, ₽", "interest_balance_source"),
    ("Источник компонентов остатка", "financial_source_label"),
    ("Остаток в снимке, ₽ — не текущий", "reported_balance"),
    ("Обновление у источника", "updated"),
    ("Дата отчёта / сверки", "report_date"),
    ("Лимит, ₽ — не выданная сумма", "limit"),
    ("Просрочка по отчёту, ₽", "overdue"),
    ("Срочный основной долг, ₽", "principal_not_due"),
    ("Источник снимка", "bureau"),
    ("Первоначальный кредитор", "original_creditor"),
    ("Новый кредитор по уступке", "assignee"),
    ("Представитель / коллектор", "representative"),
    ("Сведения о передаче", "assignment"),
    ("Звонки (оценка владельца)", "calls"),
    ("Заметки о звонках", "call_notes"),
    ("Текущее состояние (ручное)", "status_label"),
    ("Уточнения", "note"),
    ("Пояснение к снимку", "source_note"),
    ("Документов", "documents"),
]


def xlsx(request):
    _, rows, _ = query_rows(request)
    book = Workbook()
    sheet = book.active
    sheet.title = "Реестр"
    sheet.append([name for name, _ in EXPORT_COLUMNS])
    for row in rows:
        sheet.append([row.get(key) for _, key in EXPORT_COLUMNS])
        for cell in sheet[sheet.max_row]:
            # Force literal text even for =, +, -, @ and hyperlink-like strings.
            if isinstance(cell.value, str):
                cell.data_type = "s"
            elif isinstance(cell.value, date):
                cell.number_format = "DD.MM.YYYY"
            elif cell.value is not None:
                cell.number_format = (
                    "0"
                    if EXPORT_COLUMNS[cell.column - 1][1] == "documents"
                    else "#,##0.00"
                )
    sheet.freeze_panes = "B2"
    sheet.auto_filter.ref = sheet.dimensions
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="314426")
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    sheet.row_dimensions[1].height = 48
    for column in sheet.columns:
        sheet.column_dimensions[column[0].column_letter].width = (
            24 if column[0].column > 1 else 45
        )
    note = book.create_sheet("Пояснение")
    note.append(["Снимки БКИ относятся к датам источника, а не к текущему дню."])
    note.append(
        [
            "Неизвестное оставлено пустым. Лимит, выданная сумма и остаток не складываются."
        ]
    )
    note.append(
        ["Погашено не рассчитывается вычитанием остатка из первоначальной суммы."]
    )
    note.append(
        [
            "Связь с ручной записью по названию не подтверждает UID; звонок не доказывает уступку."
        ]
    )
    note.column_dimensions["A"].width = 115
    stream = BytesIO()
    book.save(stream)
    response = HttpResponse(
        stream.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        'attachment; filename="private-credit-register.xlsx"'
    )
    return response

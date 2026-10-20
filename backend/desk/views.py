import json
from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import connection
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import DeskAuthenticationForm, ImportForm, record_form
from .models import (
    Change,
)
from .obligation_presentation import obligation_data, prepare_obligations
from .presentation import calendar_rows, href, money, today_context
from .security import is_owner, reserve_login, reset_login_guard, safe_next
from .services import (
    ENTITIES,
    dump,
    export_records,
    import_records,
    paid_amount,
    read_records,
    remaining,
    save_record,
)


def page(request, template, context=None, *, status=200):
    return render(
        request,
        "desk/" + template + ".html",
        {"entities": ENTITIES, **(context or {})},
        status=status,
    )


def sign_in(request):
    if is_owner(request.user):
        return redirect("/")
    form = DeskAuthenticationForm(
        request, data=request.POST if request.method == "POST" else None
    )
    status = 200
    if request.method == "POST":
        if not reserve_login():
            form.throttled = True
            form.is_valid()
            status = 429
        elif form.is_valid() and is_owner(form.get_user()):
            login(request, form.get_user())
            reset_login_guard()
            return redirect(safe_next(request))
        else:
            form.add_error(None, "Не удалось войти. Проверьте имя и пароль.")
    return page(
        request,
        "login",
        {"form": form, "next": safe_next(request), "title": "Вход в кабинет"},
        status=status,
    )


@require_POST
def sign_out(request):
    logout(request)
    return redirect("/login/")


def password(request):
    form = PasswordChangeForm(
        request.user, request.POST if request.method == "POST" else None
    )
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Пароль изменён.")
        return redirect("/")
    return page(request, "password", {"form": form, "title": "Пароль владельца"})


def today(request):
    window = 30 if request.GET.get("window") == "30" else 7
    return page(request, "today", {**today_context(window), "title": "Сегодня"})


def calendar(request):
    days = 90 if request.GET.get("days") == "90" else 30
    return page(
        request,
        "calendar",
        {"title": "Календарь", "rows": calendar_rows(days), "days": days},
    )


def entity_info(entity):
    if entity not in ENTITIES:
        raise Http404
    return ENTITIES[entity]


def row_data(entity, record):
    detail, amount = "", None
    if entity == "task":
        detail = record.get_status_display() + " · " + record.get_priority_display()
    elif entity == "project":
        detail = record.get_status_display() + (
            " · " + record.next_step if record.next_step else ""
        )
    elif entity == "contact":
        detail = record.channel + (" · " + record.next_step if record.next_step else "")
    elif entity == "obligation":
        return {
            "record": record,
            "url": href(entity, record),
            "title": str(record),
            "obligation": obligation_data(record),
        }
    elif entity in ("payment", "expected"):
        paid = paid_amount(record)
        left = remaining(record)
        amount = money(left) + (" осталось" if left is not None else "")
        detail = "В журнале: " + money(paid) + "; план: " + money(record.amount)
        if record.metadata.get("reported_payment"):
            detail += " · Есть сообщение о переводе, требует проверки"
        if entity == "payment":
            detail += " · " + (
                "Черновик: сумма / дата не подтверждены"
                if not record.confirmed
                else "Оплачено"
                if not left
                else "Частично оплачено"
                if paid
                else "Не оплачено"
            )
        else:
            detail += (
                " · " + record.get_status_display() + " · " + record.get_track_display()
            )
    elif entity == "transaction":
        amount = money(record.amount)
        detail = record.get_direction_display() + (
            " · " + record.get_track_display() if record.direction == "income" else ""
        )
    elif entity == "addon":
        detail = record.get_status_display() + " · " + record.company
        amount = money(record.reported_amount) + " — сообщено, не операция"
    elif entity == "email":
        detail = record.email + (
            " · проверено " + record.verified_on.strftime("%d.%m.%Y")
            if record.verified_on
            else " · дата проверки неизвестна"
        )
    elif entity == "reference":
        detail = record.get_kind_display() + " · Вне денежных расчётов"
    return {
        "record": record,
        "url": href(entity, record),
        "title": str(record),
        "detail": detail,
        "amount": amount,
        "date": getattr(record, "due_date", getattr(record, "date", None)),
    }


def records(request, entity):
    model, plural, singular = entity_info(entity)
    query = model.objects.all()
    if entity != "obligation":
        query = query.filter(archived=request.GET.get("archived") == "1")
    q = request.GET.get("q", "")[:120]
    if q and entity != "obligation":
        field = "name" if entity in ("contact", "project") else "title"
        query = query.filter(**{field + "__icontains": q})
    filters = {}
    for field in ("status", "track"):
        if any(f.name == field for f in model._meta.fields):
            filters[field] = model._meta.get_field(field).choices
            if request.GET.get(field):
                query = query.filter(**{field: request.GET[field]})
    if entity == "transaction" and request.GET.get("date"):
        try:
            query = query.filter(date=date.fromisoformat(request.GET["date"]))
        except ValueError:
            query = query.none()
    if entity == "task" and request.GET.get("overdue") == "1":
        query = query.filter(due_date__lt=timezone.localdate()).exclude(status="done")
    for field in model._meta.fields:
        if field.is_relation and request.GET.get(field.name, "").isdigit():
            query = query.filter(**{field.attname: int(request.GET[field.name])})
    if entity == "obligation":
        rows = [row_data(entity, obj) for obj in prepare_obligations(query)]
        if q:
            # SQLite LIKE does not case-fold Cyrillic, and raw JSON may escape it.
            needle = q.casefold()
            rows = [
                row
                for row in rows
                if needle
                in (
                    row["title"]
                    + " "
                    + row["record"].notes
                    + " "
                    + json.dumps(row["record"].metadata, ensure_ascii=False)
                ).casefold()
            ]
        state = request.GET.get(
            "state", "archived" if request.GET.get("archived") == "1" else "active"
        )
        if state == "paid":
            rows = [r for r in rows if r["obligation"]["paid_reported"]]
        elif state == "archived":
            rows = [r for r in rows if r["record"].archived]
        elif state != "all":
            rows = [
                r
                for r in rows
                if not r["record"].archived and not r["obligation"]["paid_reported"]
            ]
        check = request.GET.get("check")
        if check in ("needs_check", "has_balance"):
            rows = [r for r in rows if r["obligation"][check]]
        elif check == "service":
            rows = [r for r in rows if r["obligation"]["service_note"]]
        order = request.GET.get("order", "date")
        if order == "name":
            rows.sort(key=lambda r: (r["title"].casefold(), r["record"].pk))
        else:
            rows.sort(
                key=lambda r: (
                    r["obligation"]["next_date"] or date.max,
                    r["title"].casefold(),
                    r["record"].pk,
                )
            )
        objects = Paginator(rows, 50).get_page(request.GET.get("page"))
        page_rows = list(objects)
    else:
        objects = Paginator(query, 50).get_page(request.GET.get("page"))
        page_rows = [row_data(entity, obj) for obj in objects]
    params = request.GET.copy()
    params.pop("page", None)
    return page(
        request,
        "records",
        {
            "title": plural,
            "entity": entity,
            "singular": singular,
            "rows": page_rows,
            "objects": objects,
            "filters": filters,
            "q": q,
            "query_params": params.urlencode(),
            "form_relations": [
                {"name": f.name, "value": request.GET[f.name]}
                for f in model._meta.fields
                if f.is_relation and request.GET.get(f.name, "").isdigit()
            ],
        },
    )


def edit(request, entity, pk=None):
    model, plural, singular = entity_info(entity)
    instance = get_object_or_404(model, pk=pk) if pk else None
    form = record_form(
        entity,
        data=request.POST if request.method == "POST" else None,
        instance=instance,
    )
    if not instance:
        for field in model._meta.fields:
            if field.is_relation and request.GET.get(field.name, "").isdigit():
                form.initial[field.name] = int(request.GET[field.name])
        if entity == "transaction":
            form.initial["date"] = timezone.localdate()
            if request.GET.get("payment", "").isdigit():
                form.initial["direction"] = "expense"
            elif request.GET.get("expected", "").isdigit():
                form.initial["direction"] = "income"
    if request.method == "POST":
        try:
            if request.POST.get("action") in ("archive", "restore") and instance:
                save_record(
                    entity,
                    {"archived": request.POST["action"] == "archive"},
                    actor=request.user.username,
                    instance=instance,
                )
                messages.success(
                    request,
                    "Запись в архиве."
                    if request.POST["action"] == "archive"
                    else "Запись восстановлена.",
                )
                return redirect(f"/records/{entity}/")
            if form.is_valid():
                if (
                    instance
                    and form.cleaned_data.get("revision")
                    != instance.updated_at.isoformat()
                ):
                    form.add_error(
                        None,
                        "Запись уже изменена. Обновите страницу перед сохранением.",
                    )
                else:
                    values = {
                        name: (value.pk if hasattr(value, "pk") else value)
                        for name, value in form.cleaned_data.items()
                        if name != "revision"
                    }
                    record, _ = save_record(
                        entity, values, actor=request.user.username, instance=instance
                    )
                    messages.success(request, "Сохранено.")
                    return redirect(href(entity, record))
        except ValidationError as error:
            form.add_error(None, "; ".join(error.messages))
    related = []
    documents = []
    document_link = ""
    if instance:
        for kind, (related_model, _, _) in ENTITIES.items():
            field = next(
                (
                    f
                    for f in related_model._meta.fields
                    if f.is_relation and f.related_model == model
                ),
                None,
            )
            if field:
                related.extend(
                    row_data(kind, obj)
                    for obj in related_model.objects.filter(**{field.name: instance})[
                        :30
                    ]
                )
    if instance:
        from .models import Document

        field = next(
            (
                f
                for f in Document._meta.fields
                if f.is_relation and f.related_model == model
            ),
            None,
        )
        if field:
            documents = Document.objects.filter(
                archived=False, **{field.name: instance}
            )
            document_link = f"/documents/new/?{field.name}={instance.pk}"
    return page(
        request,
        "edit",
        {
            "title": ("Изменить: " if instance else "Добавить: ") + singular,
            "entity": entity,
            "plural": plural,
            "form": form,
            "record": instance,
            "summary": row_data(entity, instance) if instance else None,
            "history": Change.objects.filter(entity=entity, record_id=pk)[:20]
            if pk
            else [],
            "metadata": json.dumps(instance.metadata, ensure_ascii=False, indent=2)
            if instance and instance.metadata
            else "",
            "related": related,
            "documents": documents,
            "document_link": document_link,
        },
    )


def data_tools(request):
    form = ImportForm(request.POST or None, request.FILES or None)
    preview, token = None, ""
    if request.method == "POST":
        try:
            if request.POST.get("token"):
                payload = signing.loads(
                    request.POST["token"], salt="desk-import", max_age=900
                )
                if payload["owner"] != request.user.pk:
                    raise ValidationError("Предпросмотр относится к другому владельцу.")
                results = import_records(
                    payload["records"], actor=request.user.username, dry_run=False
                )
                messages.success(
                    request,
                    f"Импорт завершён: {len(results)} строк, изменено {sum(r['changed'] for r in results)}.",
                )
                return redirect("/data/")
            if form.is_valid():
                records = read_records(
                    form.cleaned_data["file"].read(),
                    form.cleaned_data["format"],
                    source=form.cleaned_data["source"],
                    batch=form.cleaned_data["batch"],
                    entity=form.cleaned_data["entity"],
                )
                preview = import_records(
                    records, actor=request.user.username, dry_run=True
                )
                token = signing.dumps(
                    {"owner": request.user.pk, "records": dump(records)},
                    salt="desk-import",
                    compress=True,
                )
        except (ValidationError, signing.BadSignature, KeyError, ValueError) as error:
            form.add_error(
                None,
                "; ".join(error.messages)
                if isinstance(error, ValidationError)
                else "Предпросмотр недействителен. Загрузите файл заново.",
            )
    return page(
        request,
        "data",
        {"title": "Данные и перенос", "form": form, "preview": preview, "token": token},
    )


def export(request):
    response = JsonResponse(export_records(), json_dumps_params={"ensure_ascii": False})
    response["Content-Disposition"] = 'attachment; filename="rexileer-desk-export.json"'
    return response


def history(request):
    changes = Change.objects.all()
    entity = request.GET.get("entity")
    if entity in ENTITIES or entity == "document":
        changes = changes.filter(entity=entity)
    if request.GET.get("record", "").isdigit():
        changes = changes.filter(record_id=int(request.GET["record"]))
    objects = Paginator(changes, 30).get_page(request.GET.get("page"))
    return page(request, "history", {"title": "Журнал изменений", "objects": objects})


def asset(request, name):
    fonts = Path(settings.BASE_DIR).parent / "site" / "assets" / "fonts"
    if not fonts.is_dir():
        fonts = Path(settings.BASE_DIR) / "site" / "assets" / "fonts"
    allowed = {
        "desk.css": (Path(__file__).parent / "static" / "desk.css", "text/css"),
        "fonts/fonts.css": (fonts / "fonts.css", "text/css"),
    }
    for file in ("7635422bd10d", "08949f728dc5", "c268b459a932", "a30ddcd34970"):
        allowed[f"fonts/{file}.woff2"] = (fonts / (file + ".woff2"), "font/woff2")
    if name not in allowed:
        raise Http404
    path, mime = allowed[name]
    return HttpResponse(path.read_bytes(), content_type=mime)


def health(request):
    if request.META.get("REMOTE_ADDR") not in ("127.0.0.1", "::1") and not is_owner(
        request.user
    ):
        raise Http404
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"ok": True})


def robots(request):
    return HttpResponse("User-agent: *\nDisallow: /\n", content_type="text/plain")

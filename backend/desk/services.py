"""One validation and audit path for HTML forms, private CLI and imports."""

import csv
import io
import json
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection, models, transaction

from .models import (
    ZERO,
    Addon,
    Change,
    Contact,
    CreditorEmail,
    ExpectedIncome,
    Letter,
    Obligation,
    PlannedPayment,
    Project,
    Reference,
    Task,
    Transaction,
)

ENTITIES = {
    "contact": (Contact, "Контакты", "Контакт"),
    "project": (Project, "Проекты", "Проект"),
    "task": (Task, "Задачи", "Задача"),
    "obligation": (Obligation, "Обязательства", "Обязательство"),
    "payment": (PlannedPayment, "Плановые платежи", "Плановый платёж"),
    "expected": (ExpectedIncome, "Ожидаемые поступления", "Ожидаемое поступление"),
    "transaction": (Transaction, "Операции", "Операция"),
    "reference": (Reference, "Справки и заявки (вне учёта)", "Справочная запись"),
    "addon": (Addon, "Допуслуги и возвраты", "Допуслуга"),
    "email": (CreditorEmail, "Почты кредиторов", "Контактный адрес"),
    "letter": (Letter, "Письма и ответы", "Письмо / ответ"),
}
ORDER = {name: index for index, name in enumerate(ENTITIES)}
SYSTEM = {"id", "created_at", "updated_at"}


def workspace_lock():
    # First operation is a write: SQLite waits for the writer instead of a
    # read-to-write lock upgrade. All financial/import/blob writes serialize.
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT OR IGNORE INTO desk_workspacelock (id, revision) VALUES (1, 0)"
        )
        cursor.execute(
            "UPDATE desk_workspacelock SET revision = revision + 1 WHERE id = 1"
        )


def dump(value):
    return json.loads(json.dumps(value, cls=DjangoJSONEncoder, ensure_ascii=False))


def snapshot(instance):
    return {
        f.name: dump(getattr(instance, f.attname))
        for f in instance._meta.fields
        if f.name not in SYSTEM
    }


def total(values):
    return sum(values, ZERO).quantize(Decimal("0.01"))


def current_balance(obligation):
    if obligation.balance is None:
        return None
    paid = Transaction.objects.filter(
        archived=False,
        confirmed=True,
        obligation=obligation,
        date__gt=obligation.balance_as_of,
    )
    return obligation.balance - total(paid.values_list("principal", flat=True))


def paid_amount(record):
    field = "expected" if isinstance(record, ExpectedIncome) else "payment"
    return total(
        Transaction.objects.filter(
            archived=False, confirmed=True, **{field: record}
        ).values_list("amount", flat=True)
    )


def remaining(record):
    if record.amount is None:
        return None
    return max(ZERO, record.amount - paid_amount(record))


def editable_fields(model):
    return [f for f in model._meta.fields if f.name not in SYSTEM]


def resolve(field, value):
    if value in (None, ""):
        return None if field.null else ""
    if isinstance(field, models.ForeignKey):
        if isinstance(value, dict) and set(value) == {"source", "external_id"}:
            try:
                return field.related_model.objects.get(**value).pk
            except field.related_model.DoesNotExist:
                raise ValidationError(
                    f"Связанная запись {field.name} не найдена."
                ) from None
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValidationError(
                f"Связь {field.name}: нужен ID или source/external_id."
            )
    if isinstance(field, models.DecimalField) and isinstance(value, (float, bool)):
        raise ValidationError("Передавайте денежные значения строкой с копейками.")
    if isinstance(field, models.BooleanField) and not isinstance(value, bool):
        if value not in ("true", "false", "0", "1"):
            raise ValidationError("Архив: ожидается true/false.")
        return value in ("true", "1")
    return field.to_python(value)


@transaction.atomic
def save_record(entity, fields, *, actor, instance=None):
    workspace_lock()
    if entity not in ENTITIES or not isinstance(fields, dict):
        raise ValidationError("Неизвестный тип записи или формат полей.")
    model = ENTITIES[entity][0]
    if instance is not None:
        instance = model.objects.select_for_update().get(pk=instance.pk)
    before = snapshot(instance) if instance else {}
    instance = instance or model()
    allowed = {f.name: f for f in editable_fields(model)}
    if set(fields) - allowed.keys():
        raise ValidationError(
            "Неизвестные поля: " + ", ".join(sorted(set(fields) - allowed.keys()))
        )
    for name, value in fields.items():
        field = allowed[name]
        setattr(instance, field.attname, resolve(field, value))
    # Reject invalid individual values before cross-field arithmetic runs.
    for field in allowed.values():
        setattr(
            instance,
            field.attname,
            field.clean(getattr(instance, field.attname), instance),
        )
    instance.full_clean()
    if len(
        json.dumps(instance.metadata, cls=DjangoJSONEncoder)
    ) > 64000 or not isinstance(instance.metadata, dict):
        raise ValidationError("Данные источника: объект не больше 64 КБ.")
    for field in allowed.values():
        if isinstance(field, models.ForeignKey) and getattr(instance, field.attname):
            related = getattr(instance, field.name)
            if related.archived and before.get(field.name) != related.pk:
                raise ValidationError(
                    f"Связанная запись «{field.verbose_name}» в архиве."
                )
    if isinstance(instance, Transaction) and instance.expected_id:
        instance.track = instance.expected.track
        if (
            instance.project_id
            and instance.expected.project_id
            and instance.project_id != instance.expected.project_id
        ):
            raise ValidationError("Ожидание относится к другому проекту.")
        instance.project_id = instance.project_id or instance.expected.project_id
    if before == snapshot(instance):
        return instance, False
    instance.save()
    # A dated confirmed snapshot is independent of plans. Only explicit actual
    # principal AFTER that date adjusts it. Unknown remains unknown.
    obligations = []
    if isinstance(instance, Obligation):
        obligations.append(instance)
    if isinstance(instance, Transaction):
        for addon in Addon.objects.filter(actual_income=instance):
            addon.full_clean()
        ids = {before.get("obligation"), instance.obligation_id} - {None}
        obligations.extend(Obligation.objects.filter(pk__in=ids))
    for obligation in obligations:
        balance = current_balance(obligation)
        if balance is not None and balance < ZERO:
            raise ValidationError(
                "Основной долг после даты снимка превышает подтверждённый остаток. Проверьте сумму и дату."
            )
    Change.objects.create(
        entity=entity,
        record_id=instance.pk,
        actor=actor[:100],
        before=before,
        after=snapshot(instance),
    )
    return instance, True


def read_records(raw, format="json", *, source="import", batch="", entity=""):
    if len(raw) > 2 * 1024 * 1024:
        raise ValidationError("Файл больше 2 МБ.")
    try:
        text = raw.decode("utf-8-sig")
        if format == "csv":
            records = []
            for row in csv.DictReader(io.StringIO(text)):
                kind = row.pop("entity", "") or entity
                origin = row.pop("source", "") or source
                external = row.pop("external_id", "")
                import_batch = row.pop("import_batch", "") or batch
                fields = {k: v for k, v in row.items() if v != ""}
                for key, value in list(fields.items()):
                    if value.startswith("{"):
                        fields[key] = json.loads(value, parse_float=Decimal)
                records.append(
                    {
                        "entity": kind,
                        "source": origin,
                        "external_id": external,
                        "import_batch": import_batch,
                        "fields": fields,
                    }
                )
        else:
            payload = json.loads(text, parse_float=Decimal)
            if not isinstance(payload, dict) or payload.get("version") != 1:
                raise ValidationError("Нужен JSON-объект с version: 1 и records.")
            records = payload.get("records")
        if not isinstance(records, list) or not 1 <= len(records) <= 1000:
            raise ValidationError("Нужны от 1 до 1000 записей.")
        return records
    except (ValueError, UnicodeError, AttributeError, TypeError, csv.Error):
        raise ValidationError(
            "Не удалось прочитать UTF-8 JSON/CSV. Проверьте формат файла."
        ) from None


@transaction.atomic
def import_records(records, *, actor, dry_run=True):
    workspace_lock()
    results = []
    seen = set()
    if not isinstance(records, list) or not 1 <= len(records) <= 1000:
        raise ValidationError("Нужны от 1 до 1000 записей.")
    # Preserve same-source references even when a file lists children first.
    for row in sorted(
        records,
        key=lambda item: (
            ORDER.get(item.get("entity"), 99) if isinstance(item, dict) else 99
        ),
    ):
        if not isinstance(row, dict) or set(row) - {
            "entity",
            "source",
            "external_id",
            "import_batch",
            "fields",
        }:
            raise ValidationError("Неизвестный формат строки импорта.")
        kind = row.get("entity")
        if kind not in ENTITIES or not row.get("source") or not row.get("external_id"):
            raise ValidationError("Каждой строке нужны entity, source и external_id.")
        key = (kind, row["source"], row["external_id"])
        if key in seen:
            raise ValidationError("Один внешний ID повторён в файле. Импорт отменён.")
        seen.add(key)
        model = ENTITIES[kind][0]
        origin = {"source": row["source"], "external_id": row["external_id"]}
        instance = model.objects.filter(**origin).first()
        fields = row.get("fields", {})
        if not isinstance(fields, dict) or set(fields) & {
            "source",
            "external_id",
            "import_batch",
        }:
            raise ValidationError("Происхождение укажите на уровне строки, вне fields.")
        values = {**fields, **origin, "import_batch": row.get("import_batch", "")}
        record, changed = save_record(kind, values, actor=actor, instance=instance)
        results.append(
            {
                "entity": kind,
                "external_id": record.external_id,
                "id": record.pk,
                "changed": changed,
                "title": str(record),
            }
        )
    if dry_run:
        transaction.set_rollback(True)
    return results


def export_records():
    records = []
    for entity, (model, _, _) in ENTITIES.items():
        for record in model.objects.order_by("pk").iterator():
            fields = snapshot(record)
            for name in ("source", "external_id", "import_batch"):
                fields.pop(name)
            for f in model._meta.fields:
                if isinstance(f, models.ForeignKey) and getattr(record, f.attname):
                    related = getattr(record, f.name)
                    fields[f.name] = {
                        "source": related.source,
                        "external_id": related.external_id,
                    }
            records.append(
                {
                    "entity": entity,
                    "source": record.source,
                    "external_id": record.external_id,
                    "import_batch": record.import_batch,
                    "fields": fields,
                }
            )
    from .models import Document

    documents = [
        {"source": d.source, "external_id": d.external_id, "fields": snapshot(d)}
        for d in Document.objects.order_by("pk").iterator()
    ]
    return {
        "version": 1,
        "records": records,
        "attachments_included": False,
        "document_metadata": documents,
    }

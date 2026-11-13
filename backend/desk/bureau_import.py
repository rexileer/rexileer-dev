"""Append-only bureau evidence, independent of manually maintained money records."""

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import CreditContract, CreditSnapshot, Reference
from .services import save_record, workspace_lock


@transaction.atomic
def import_bureau(payload, *, actor, dry_run=True):
    workspace_lock()
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValidationError("Нужен пакет БКИ версии 1.")
    records = payload.get("records")
    if not isinstance(records, list) or not 1 <= len(records) <= 1000:
        raise ValidationError("Пакет: от 1 до 1000 договоров.")
    seen = set()
    result = {
        "contracts": 0,
        "created": 0,
        "snapshots_created": 0,
        "linked": 0,
        "changed": 0,
    }
    allowed = {
        "title",
        "product_kind",
        "brand",
        "kind",
        "signed_on",
        "manual_obligation",
        "link_status",
        "metadata",
        "notes",
    }
    for row in records:
        if not isinstance(row, dict):
            raise ValidationError("Некорректная строка пакета.")
        uid = row.get("uid")
        if not isinstance(uid, str) or not 8 <= len(uid) <= 100 or uid in seen:
            raise ValidationError("Нужны уникальные UID; повтор отменяет весь пакет.")
        seen.add(uid)
        fields = row.get("contract", {})
        if not isinstance(fields, dict) or set(fields) - allowed:
            raise ValidationError(
                "Пакет не может менять текущие деньги, ставки или ручные оценки."
            )
        credit = CreditContract.objects.filter(uid=uid).first()
        if credit is None:
            credit, _ = save_record(
                "credit",
                {
                    **fields,
                    "uid": uid,
                    "source": "bki",
                    "external_id": uid,
                    "import_batch": payload.get("batch", ""),
                },
                actor=actor,
            )
            result["created"] += 1
            result["changed"] += 1
        # Subsequent imports never overwrite manual contract refinements/links.
        evidence = row.get("snapshot")
        if (
            not isinstance(evidence, dict)
            or not evidence.get("bureau")
            or not evidence.get("report_date")
        ):
            raise ValidationError("Каждому договору нужен датированный снимок.")
        if set(evidence) & {"source", "external_id", "credit", "archived"}:
            raise ValidationError("Происхождение и договор снимка задаются импортом.")
        external_id = uid + ":" + evidence["report_date"] + ":" + evidence["bureau"]
        old = CreditSnapshot.objects.filter(
            source="bki", external_id=external_id
        ).first()
        _, changed = save_record(
            "credit_snapshot",
            {
                **evidence,
                "credit": credit.pk,
                "source": "bki",
                "external_id": external_id,
                "import_batch": payload.get("batch", ""),
            },
            actor=actor,
            instance=old,
        )
        result["snapshots_created"] += int(old is None)
        result["changed"] += int(changed)
        result["linked"] += int(bool(credit.manual_obligation_id))
        result["contracts"] += 1
    if payload.get("summary"):
        _, changed = save_record(
            "reference",
            {
                "source": "bki",
                "external_id": "bureau-scope-" + payload.get("batch", "report"),
                "title": "БКИ: состав и ограничения датированного реестра",
                "kind": "information",
                "metadata": payload["summary"],
                "notes": "Отчётные сведения не являются текущим долгом, нижней границей или суммой погашения сегодня. Исторические отчёты не прибавляются повторно.",
            },
            actor=actor,
            instance=Reference.objects.filter(
                source="bki",
                external_id="bureau-scope-" + payload.get("batch", "report"),
            ).first(),
        )
        result["changed"] += int(changed)
    if dry_run:
        transaction.set_rollback(True)
    return result

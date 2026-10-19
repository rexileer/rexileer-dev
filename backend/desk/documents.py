import hashlib
import io
import os
import re
import shutil
import warnings
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from PIL import Image

from .models import Change, Document
from .services import snapshot, workspace_lock

MIMES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}
DOCUMENT_FIELDS = [
    "title",
    "kind",
    "document_date",
    "obligation",
    "payment",
    "addon",
    "letter",
    "email",
    "transaction",
    "evidence_status",
    "notes",
]


def cipher():
    return Fernet(settings.DOCUMENT_KEY.encode("ascii"))


def blob_path(key, root=None):
    if not re.fullmatch(r"[a-f0-9]{32}", key):
        raise ValidationError("Некорректный ключ файла.")
    return Path(root or settings.DOCUMENT_ROOT) / (key + ".fernet")


def validate_file(name, content_type, raw):
    if (
        not name
        or len(name) > 250
        or any(ord(c) < 32 or c == "\x7f" for c in name)
        or any(s in name for s in ("/", "\\", ".."))
    ):
        raise ValidationError("Недопустимое имя файла.")
    suffix = Path(name).suffix.lower()
    if suffix not in MIMES or content_type != MIMES[suffix]:
        raise ValidationError(
            "Разрешены только PDF, JPEG и PNG с соответствующим типом файла."
        )
    if not raw or len(raw) > settings.DOCUMENT_MAX_BYTES:
        raise ValidationError("Файл пуст или превышает 10 МБ.")
    if suffix == ".pdf":
        if not raw.startswith(b"%PDF-") or b"%%EOF" not in raw[-1024:]:
            raise ValidationError("Сигнатура PDF не соответствует файлу.")
    else:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(raw)) as image:
                    if (
                        image.format != ("PNG" if suffix == ".png" else "JPEG")
                        or image.width * image.height > 20000000
                    ):
                        raise ValueError
                    image.verify()
        except (
            OSError,
            ValueError,
            SyntaxError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
        ):
            raise ValidationError(
                "Изображение повреждено, подменено или слишком велико по разрешению."
            ) from None
    return MIMES[suffix]


@transaction.atomic
def upload_document(
    fields, file, *, actor, source="desk", external_id=None, dry_run=False
):
    workspace_lock()
    raw = file.read(settings.DOCUMENT_MAX_BYTES + 1)
    mime = validate_file(file.name, file.content_type, raw)
    digest = hashlib.sha256(raw).hexdigest()
    if Document.objects.filter(sha256=digest).exists():
        raise ValidationError(
            "Такой файл уже сохранён, в том числе возможен архив. Дубликат не загружен."
        )
    if set(fields) - set(DOCUMENT_FIELDS):
        raise ValidationError("Неизвестные поля документа.")
    document = Document(
        **fields,
        original_name=file.name,
        content_type=mime,
        size=len(raw),
        sha256=digest,
        source=source,
    )
    if external_id:
        document.external_id = external_id
    document.full_clean()
    if dry_run:
        transaction.set_rollback(True)
        return document
    root = Path(settings.DOCUMENT_ROOT)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    existing = sum(p.stat().st_size for p in root.glob("*.fernet"))
    token = cipher().encrypt(raw)
    if (
        existing + len(token) > settings.DOCUMENT_QUOTA_BYTES
        or shutil.disk_usage(root).free < len(token) + 512 * 1024 * 1024
    ):
        raise ValidationError(
            "Недостаточно свободного места или достигнут лимит хранилища (512 МБ зашифрованных файлов)."
        )
    target = blob_path(document.storage_key)
    with os.fdopen(
        os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb"
    ) as stream:
        stream.write(token)
        stream.flush()
        os.fsync(stream.fileno())
    # Immutable ciphertext is complete before a committed row can reference it.
    document.save()
    Change.objects.create(
        entity="document",
        record_id=document.pk,
        actor=actor[:100],
        before={},
        after=snapshot(document),
    )
    return document


def decrypt_document(document):
    try:
        token = blob_path(document.storage_key).read_bytes()
        if len(token) > settings.DOCUMENT_MAX_BYTES * 2:
            raise ValueError
        raw = cipher().decrypt(token)
        if hashlib.sha256(raw).hexdigest() != document.sha256:
            raise ValueError
        return raw
    except (OSError, InvalidToken, ValueError):
        raise ValidationError(
            "Документ недоступен: проверьте закрытое хранилище и его ключ. Содержимое не раскрыто."
        ) from None


@transaction.atomic
def edit_document(document, fields, *, actor):
    workspace_lock()
    document = Document.objects.select_for_update().get(pk=document.pk)
    if set(fields) - (set(DOCUMENT_FIELDS) | {"archived"}):
        raise ValidationError(
            "Исходный файл нельзя заменить. Добавьте новую запись и сохраните историю."
        )
    before = snapshot(document)
    for key, value in fields.items():
        setattr(document, key, value)
    document.full_clean()
    after = snapshot(document)
    if after != before:
        document.save()
        Change.objects.create(
            entity="document",
            record_id=document.pk,
            actor=actor[:100],
            before=before,
            after=after,
        )
    return document

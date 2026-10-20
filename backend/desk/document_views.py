from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import content_disposition_header

from .documents import DOCUMENT_FIELDS, decrypt_document, edit_document, upload_document
from .forms import DocumentForm
from .models import Addon, Change, Document, Obligation
from .obligation_presentation import document_obligation_filter
from .views import page


def documents(request):
    records = Document.objects.filter(archived=request.GET.get("archived") == "1")
    q = request.GET.get("q", "")[:120]
    if q:
        records = records.filter(Q(title__icontains=q) | Q(notes__icontains=q))
    if request.GET.get("kind"):
        records = records.filter(kind=request.GET["kind"])
    if request.GET.get("obligation", "").isdigit():
        records = records.filter(
            document_obligation_filter(int(request.GET["obligation"]))
        ).distinct()
    for key in ("addon",):
        if request.GET.get(key, "").isdigit():
            records = records.filter(**{key + "_id": request.GET[key]})
    for key, lookup in (("from", "document_date__gte"), ("to", "document_date__lte")):
        if request.GET.get(key):
            try:
                from datetime import date

                records = records.filter(
                    **{lookup: date.fromisoformat(request.GET[key])}
                )
            except ValueError:
                records = records.none()
    objects = Paginator(records, 50).get_page(request.GET.get("page"))
    return page(
        request,
        "documents",
        {
            "title": "Документы",
            "objects": objects,
            "kinds": Document.KINDS,
            "obligations": Obligation.objects.filter(archived=False),
            "addons": Addon.objects.filter(archived=False),
        },
    )


def document(request, pk=None):
    record = get_object_or_404(Document, pk=pk) if pk else None
    initial = {
        name: request.GET[name]
        for name in ("obligation", "addon", "payment", "letter", "email", "transaction")
        if request.GET.get(name, "").isdigit()
    }
    form = DocumentForm(
        request.POST or None, request.FILES or None, instance=record, initial=initial
    )
    if request.method == "POST":
        try:
            if request.POST.get("action") in ("archive", "restore") and record:
                edit_document(
                    record,
                    {"archived": request.POST["action"] == "archive"},
                    actor=request.user.username,
                )
                messages.success(
                    request,
                    "Документ сохранён в архиве."
                    if request.POST["action"] == "archive"
                    else "Документ восстановлен.",
                )
                return redirect("/documents/")
            if form.is_valid():
                fields = {key: form.cleaned_data[key] for key in DOCUMENT_FIELDS}
                if record:
                    record = edit_document(record, fields, actor=request.user.username)
                else:
                    record = upload_document(
                        fields, form.cleaned_data["file"], actor=request.user.username
                    )
                messages.success(
                    request, "Документ сохранён. Денежных операций не создано."
                )
                return redirect(f"/documents/{record.pk}/")
        except ValidationError as error:
            form.add_error(None, "; ".join(error.messages))
    return page(
        request,
        "document",
        {
            "title": record.title if record else "Добавить документ",
            "form": form,
            "document": record,
            "history": Change.objects.filter(entity="document", record_id=record.pk)[
                :20
            ]
            if record
            else [],
        },
    )


def document_bytes(request, pk, mode):
    document = get_object_or_404(Document, pk=pk)
    try:
        raw = decrypt_document(document)
    except ValidationError as error:
        return HttpResponse(
            error.messages[0], status=503, content_type="text/plain; charset=utf-8"
        )
    response = HttpResponse(raw, content_type=document.content_type)
    suffix = {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg"}[
        document.content_type
    ]
    response["Content-Disposition"] = content_disposition_header(
        mode == "download", "document-" + document.storage_key + suffix
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Security-Policy"] = (
        "sandbox; default-src 'none'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'"
    )
    response["X-Frame-Options"] = "SAMEORIGIN"
    return response

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

from .documents import DOCUMENT_FIELDS
from .models import Document
from .services import ENTITIES


class DeskAuthenticationForm(AuthenticationForm):
    throttled = False

    def clean(self):
        if self.throttled:
            raise forms.ValidationError(
                "Слишком много попыток. Повторите через 15 минут."
            )
        return super().clean()


def record_form(entity, *, data=None, instance=None):
    model = ENTITIES[entity][0]
    fields = [
        f.name
        for f in model._meta.fields
        if f.name
        not in {
            "id",
            "source",
            "external_id",
            "import_batch",
            "metadata",
            "archived",
            "created_at",
            "updated_at",
        }
    ]
    form_type = forms.modelform_factory(model, fields=fields)
    form = form_type(data=data, instance=instance)
    form.fields["revision"] = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        initial=instance.updated_at.isoformat() if instance else "",
    )
    for name, field in form.fields.items():
        if isinstance(field, forms.DateField):
            field.widget = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})
        if isinstance(field, forms.DecimalField):
            field.localize = True
            field.widget = forms.TextInput(
                attrs={"inputmode": "decimal", "placeholder": "0,00"}
            )
        if isinstance(field, forms.ModelChoiceField):
            existing_id = getattr(instance, name + "_id", None) if instance else None
            field.queryset = field.queryset.filter(
                Q(archived=False) | Q(pk=existing_id)
            )
        if isinstance(field.widget, forms.Textarea):
            field.widget.attrs["rows"] = 4
    return form


class ImportForm(forms.Form):
    file = forms.FileField(label="Файл JSON или CSV (UTF-8, до 2 МБ)")
    format = forms.ChoiceField(
        label="Формат", choices=[("json", "JSON v1"), ("csv", "CSV")]
    )
    source = forms.SlugField(label="Источник для CSV", initial="import", max_length=64)
    batch = forms.CharField(
        label="Название пакета для CSV", max_length=100, required=False
    )
    entity = forms.ChoiceField(
        label="Тип строк CSV (если нет колонки entity)",
        required=False,
        choices=[("", "Указан в файле")] + [(k, v[1]) for k, v in ENTITIES.items()],
    )

    def clean_file(self):
        file = self.cleaned_data["file"]
        if file.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Файл больше 2 МБ.")
        return file


class DocumentForm(forms.ModelForm):
    file = forms.FileField(
        label="PDF, JPEG или PNG, до 10 МБ",
        required=False,
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
    )

    class Meta:
        model = Document
        fields = DOCUMENT_FIELDS
        widgets = {
            "document_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields.pop("file", None)
        self.order_fields(
            [
                "file",
                "title",
                "kind",
                "document_date",
                "obligation",
                "evidence_status",
                "notes",
                "payment",
                "addon",
                "letter",
                "email",
                "transaction",
            ]
        )

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not self.instance.pk and not file:
            raise forms.ValidationError("Выберите файл.")
        if self.instance.pk and file:
            raise forms.ValidationError(
                "Исходник неизменяемый: загрузите новую запись."
            )
        if file and file.size > 10 * 1024 * 1024:
            raise forms.ValidationError("Файл больше 10 МБ.")
        return file

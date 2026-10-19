import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

ZERO = Decimal("0.00")
POSITIVE = MinValueValidator(Decimal("0.01"))


def external_id():
    return uuid.uuid4().hex


class Record(models.Model):
    source = models.CharField(
        "Источник",
        max_length=64,
        default="desk",
        validators=[RegexValidator(r"^[\w.-]+$")],
    )
    external_id = models.CharField("Внешний ID", max_length=160, default=external_id)
    import_batch = models.CharField("Пакет импорта", max_length=100, blank=True)
    metadata = models.JSONField(
        "Данные источника", default=dict, blank=True, encoder=DjangoJSONEncoder
    )
    archived = models.BooleanField("В архиве", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"], name="%(class)s_origin_unique"
            )
        ]
        ordering = ["-updated_at", "-pk"]

    def __str__(self):
        return getattr(self, "title", getattr(self, "name", "Запись"))


class Contact(Record):
    name = models.CharField("Имя / организация", max_length=200)
    channel = models.CharField("Как связаться", max_length=250, blank=True)
    next_step = models.CharField("Следующий шаг", max_length=300, blank=True)
    notes = models.TextField("Комментарий", blank=True, max_length=5000)


class Reference(Record):
    title = models.CharField("Название", max_length=250)
    kind = models.CharField(
        "Вид",
        max_length=20,
        choices=[
            ("information", "Справка источника"),
            ("rejected", "Отказ"),
            ("application", "Заявка ожидает ответа"),
        ],
        default="information",
    )
    notes = models.TextField("Сведения источника", blank=True, max_length=5000)


class Project(Record):
    name = models.CharField("Название", max_length=200)
    status = models.CharField(
        "Статус",
        max_length=20,
        default="active",
        choices=[
            ("offer", "Предложение"),
            ("active", "В работе"),
            ("waiting", "Ожидание"),
            ("done", "Завершён"),
        ],
    )
    contact = models.ForeignKey(
        Contact, verbose_name="Контакт", null=True, blank=True, on_delete=models.PROTECT
    )
    next_step = models.CharField("Следующий шаг", max_length=300, blank=True)
    notes = models.TextField("Комментарий", blank=True, max_length=5000)


TRACKS = [("new", "Новый доход"), ("existing", "Выплаты по прежней работе")]


class Task(Record):
    title = models.CharField("Задача", max_length=250)
    status = models.CharField(
        "Статус",
        max_length=20,
        default="planned",
        choices=[
            ("planned", "Запланировано"),
            ("working", "В работе"),
            ("waiting", "Ожидание"),
            ("done", "Готово"),
        ],
    )
    priority = models.PositiveSmallIntegerField(
        "Важность", default=2, choices=[(1, "Высокая"), (2, "Обычная"), (3, "Низкая")]
    )
    due_date = models.DateField("Срок", null=True, blank=True)
    minutes = models.PositiveIntegerField(
        "Оценка, минут (необязательно)",
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )
    project = models.ForeignKey(
        Project, verbose_name="Проект", null=True, blank=True, on_delete=models.PROTECT
    )
    contact = models.ForeignKey(
        Contact, verbose_name="Контакт", null=True, blank=True, on_delete=models.PROTECT
    )
    notes = models.TextField("Комментарий", blank=True, max_length=5000)


class Obligation(Record):
    title = models.CharField("Кредитор / название", max_length=250)
    contact = models.ForeignKey(
        Contact, verbose_name="Контакт", null=True, blank=True, on_delete=models.PROTECT
    )
    balance = models.DecimalField(
        "Подтверждённый остаток, ₽",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(ZERO)],
    )
    balance_as_of = models.DateField(
        "Остаток подтверждён на дату", null=True, blank=True
    )
    notes = models.TextField("Комментарий", blank=True, max_length=5000)

    def clean(self):
        from django.utils import timezone

        if (self.balance is None) != (self.balance_as_of is None):
            raise ValidationError(
                "Укажите и подтверждённый остаток, и дату; либо оставьте оба неизвестными."
            )
        if self.balance_as_of and self.balance_as_of > timezone.localdate():
            raise ValidationError(
                "Подтверждённый остаток не может быть датирован будущим."
            )


class PlannedPayment(Record):
    title = models.CharField("Назначение планового платежа", max_length=250)
    obligation = models.ForeignKey(
        Obligation, verbose_name="Обязательство", on_delete=models.PROTECT
    )
    due_date = models.DateField("Плановая дата", null=True, blank=True)
    amount = models.DecimalField(
        "Плановая сумма, ₽",
        max_digits=12,
        decimal_places=2,
        validators=[POSITIVE],
        null=True,
        blank=True,
    )
    confirmed = models.BooleanField("Сумма и дата плана подтверждены", default=False)
    notes = models.TextField("Комментарий", blank=True, max_length=5000)

    def clean(self):
        if self.confirmed and (self.amount is None or self.due_date is None):
            raise ValidationError(
                "Подтверждённому плану нужны сумма и дата. Иначе сохраните черновик."
            )


class ExpectedIncome(Record):
    title = models.CharField("За что ожидается оплата", max_length=250)
    amount = models.DecimalField(
        "Ожидаемая сумма, ₽", max_digits=12, decimal_places=2, validators=[POSITIVE]
    )
    due_date = models.DateField(
        "Ожидаемая дата (может быть неизвестна)", null=True, blank=True
    )
    status = models.CharField(
        "Статус ожидания",
        max_length=20,
        default="expected",
        choices=[
            ("expected", "Подтверждённое ожидание"),
            ("proposal", "Возможность / предложение"),
            ("cancelled", "Отменено"),
        ],
    )
    track = models.CharField(
        "Поток дохода", max_length=20, choices=TRACKS, default="existing"
    )
    project = models.ForeignKey(
        Project, verbose_name="Проект", null=True, blank=True, on_delete=models.PROTECT
    )
    contact = models.ForeignKey(
        Contact, verbose_name="Контакт", null=True, blank=True, on_delete=models.PROTECT
    )
    notes = models.TextField("Комментарий", blank=True, max_length=5000)


class Transaction(Record):
    title = models.CharField("Назначение операции", max_length=250)
    direction = models.CharField(
        "Вид", max_length=10, choices=[("income", "Приход"), ("expense", "Расход")]
    )
    amount = models.DecimalField(
        "Фактическая сумма, ₽", max_digits=12, decimal_places=2, validators=[POSITIVE]
    )
    date = models.DateField("Дата фактической операции")
    track = models.CharField(
        "Поток дохода", max_length=20, choices=TRACKS, default="existing"
    )
    project = models.ForeignKey(
        Project, verbose_name="Проект", null=True, blank=True, on_delete=models.PROTECT
    )
    contact = models.ForeignKey(
        Contact, verbose_name="Контакт", null=True, blank=True, on_delete=models.PROTECT
    )
    expected = models.ForeignKey(
        ExpectedIncome,
        verbose_name="В счёт ожидаемой оплаты",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    payment = models.ForeignKey(
        PlannedPayment,
        verbose_name="В счёт планового платежа",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    obligation = models.ForeignKey(
        Obligation,
        verbose_name="Обязательство (если погашение долга)",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    principal = models.DecimalField(
        "Из суммы точно погашено основного долга, ₽",
        max_digits=12,
        decimal_places=2,
        default=ZERO,
        validators=[MinValueValidator(ZERO)],
    )
    confirmed = models.BooleanField(
        "Подтверждаю, что операция фактически состоялась", default=False
    )
    notes = models.TextField("Комментарий", blank=True, max_length=5000)

    def clean(self):
        errors = []
        if not self.confirmed:
            errors.append(
                "В журнал можно внести только подтверждённый факт. Сообщение о переводе сохраните в примечании к плану."
            )
        if self.date:
            from django.utils import timezone

            if self.date > timezone.localdate():
                errors.append(
                    "Фактическая операция не может быть в будущем. Создайте ожидание или плановый платёж."
                )
        if self.expected_id and (
            self.direction != "income" or self.payment_id or self.obligation_id
        ):
            errors.append(
                "Ожидаемая оплата связывается только с приходом без обязательства."
            )
        if (
            self.payment_id or self.obligation_id or self.principal
        ) and self.direction != "expense":
            errors.append("Погашение обязательства связывается только с расходом.")
        if (
            self.principal is not None
            and self.amount is not None
            and self.principal > self.amount
        ):
            errors.append("Основной долг не может превышать фактическую сумму.")
        if self.payment_id:
            if not self.obligation_id:
                self.obligation_id = self.payment.obligation_id
            elif self.obligation_id != self.payment.obligation_id:
                errors.append("Плановый платёж относится к другому обязательству.")
        if self.principal and not self.obligation_id:
            errors.append(
                "Для основного долга выберите обязательство или его плановый платёж."
            )
        if errors:
            raise ValidationError(errors)


class Change(models.Model):
    entity = models.CharField(max_length=30)
    record_id = models.PositiveBigIntegerField()
    actor = models.CharField(max_length=100)
    at = models.DateTimeField(auto_now_add=True)
    before = models.JSONField(default=dict)
    after = models.JSONField(default=dict)

    class Meta:
        ordering = ["-at", "-pk"]


class LoginGuard(models.Model):
    window = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    blocked_until = models.DateTimeField(null=True)


class WorkspaceLock(models.Model):
    revision = models.PositiveBigIntegerField(default=0)


class Addon(Record):
    title = models.CharField("Допуслуга / страховка", max_length=250)
    company = models.CharField("Компания / поставщик", max_length=200, blank=True)
    obligation = models.ForeignKey(
        Obligation,
        verbose_name="Обязательство",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    reported_amount = models.DecimalField(
        "Сообщённая сумма, ₽ (не операция)",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(ZERO)],
    )
    reported_date = models.DateField("Сообщённая дата списания", null=True, blank=True)
    status = models.CharField(
        "Состояние",
        max_length=20,
        default="unverified",
        choices=[
            ("unverified", "Не проверено"),
            ("sent", "Заявление отправлено"),
            ("cancelled", "Отказ от услуги подтверждён"),
            ("refund_expected", "Возврат ожидается"),
            ("received", "Есть фактическое поступление"),
            ("refused", "В возврате отказано"),
        ],
    )
    actual_income = models.ForeignKey(
        Transaction,
        verbose_name="Полученный возврат — реальная операция",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    notes = models.TextField(
        "Основание, сроки из источника, примечание", blank=True, max_length=5000
    )

    def clean(self):
        if self.status == "received" and not self.actual_income_id:
            raise ValidationError(
                "Сначала зарегистрируйте реальный приход и свяжите его с услугой."
            )
        if self.actual_income_id and (
            self.actual_income.direction != "income"
            or not self.actual_income.confirmed
            or self.actual_income.archived
        ):
            raise ValidationError(
                "Возврат должен ссылаться на действующий подтверждённый приход."
            )


class CreditorEmail(Record):
    title = models.CharField("Назначение адреса", max_length=250)
    email = models.EmailField("Email кредитора / поставщика")
    obligation = models.ForeignKey(
        Obligation,
        verbose_name="Обязательство",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    addon = models.ForeignKey(
        Addon, verbose_name="Допуслуга", null=True, blank=True, on_delete=models.PROTECT
    )
    source_url = models.URLField("Ссылка на проверенный источник", blank=True)
    verified_on = models.DateField("Дата проверки адреса", null=True, blank=True)
    notes = models.TextField("Источник и примечание", blank=True, max_length=5000)


class Letter(Record):
    title = models.CharField("Тема письма / ответа", max_length=250)
    date = models.DateField("Дата письма", null=True, blank=True)
    email = models.ForeignKey(
        CreditorEmail,
        verbose_name="Контактный адрес",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    obligation = models.ForeignKey(
        Obligation,
        verbose_name="Обязательство",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    addon = models.ForeignKey(
        Addon, verbose_name="Допуслуга", null=True, blank=True, on_delete=models.PROTECT
    )
    notes = models.TextField(
        "Текст письма / ответа (сохранённая заметка)", max_length=20000
    )


class Document(Record):
    KINDS = [
        ("agreement", "Договор займа"),
        ("schedule", "График"),
        ("addon", "Допуслуга / страховка"),
        ("receipt", "Чек"),
        ("request", "Заявление"),
        ("response", "Ответ"),
        ("other", "Прочее"),
    ]
    title = models.CharField("Название", max_length=250)
    kind = models.CharField("Тип", max_length=20, choices=KINDS)
    document_date = models.DateField("Дата документа", null=True, blank=True)
    obligation = models.ForeignKey(
        Obligation,
        verbose_name="Обязательство",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    payment = models.ForeignKey(
        PlannedPayment,
        verbose_name="Плановый платёж",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    addon = models.ForeignKey(
        Addon, verbose_name="Допуслуга", null=True, blank=True, on_delete=models.PROTECT
    )
    letter = models.ForeignKey(
        Letter,
        verbose_name="Письмо / ответ",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    email = models.ForeignKey(
        CreditorEmail,
        verbose_name="Источник контактного адреса",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    transaction = models.ForeignKey(
        Transaction,
        verbose_name="Связанная фактическая операция",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    evidence_status = models.CharField(
        "Что подтверждает источник",
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Ожидает проверки"),
            ("sent", "Перевод отправлен"),
            ("credited", "Зачисление подтверждено"),
        ],
    )
    notes = models.TextField("Примечание и источник", blank=True, max_length=5000)
    original_name = models.CharField(max_length=250, editable=False)
    content_type = models.CharField(max_length=50, editable=False)
    size = models.PositiveIntegerField(editable=False)
    sha256 = models.CharField(max_length=64, unique=True, editable=False)
    storage_key = models.CharField(
        max_length=32, default=external_id, unique=True, editable=False
    )

    def clean(self):
        if self.payment_id:
            if self.obligation_id and self.obligation_id != self.payment.obligation_id:
                raise ValidationError(
                    "Платёж и документ относятся к разным обязательствам."
                )
            self.obligation_id = self.payment.obligation_id
        if self.addon_id and self.addon.obligation_id:
            if self.obligation_id and self.obligation_id != self.addon.obligation_id:
                raise ValidationError("Допуслуга относится к другому обязательству.")
            self.obligation_id = self.addon.obligation_id

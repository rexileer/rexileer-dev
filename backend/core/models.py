from django.db import models
from django.utils import timezone


class SiteText(models.Model):
    """Тексты сайта по ключам (data-i18n). key например: hero.title, contact.labels.email"""

    key = models.CharField(max_length=120, db_index=True)
    lang = models.CharField(
        max_length=5, choices=[("en", "English"), ("ru", "Русский")]
    )
    value = models.TextField(blank=True)

    class Meta:
        unique_together = [("key", "lang")]
        ordering = ["key", "lang"]

    def __str__(self):
        return f"{self.key} ({self.lang})"


class Skill(models.Model):
    lang = models.CharField(
        max_length=5, choices=[("en", "English"), ("ru", "Русский")]
    )
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["lang", "order"]

    def __str__(self):
        return f"{self.text} ({self.lang})"


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    slug = models.SlugField(max_length=80, unique=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PUBLISHED, db_index=True
    )
    featured = models.BooleanField(default=True)
    source_group = models.CharField(max_length=80, blank=True)
    client = models.CharField(max_length=160, blank=True)
    project_state = models.CharField(max_length=80, blank=True)
    meta_en = models.CharField(max_length=80, blank=True)
    meta_ru = models.CharField(max_length=80, blank=True)
    title_en = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)
    description_en = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    detail_en = models.TextField(blank=True)
    detail_ru = models.TextField(blank=True)
    problem_en = models.TextField(blank=True)
    problem_ru = models.TextField(blank=True)
    solution_en = models.TextField(blank=True)
    solution_ru = models.TextField(blank=True)
    result_en = models.TextField(blank=True)
    result_ru = models.TextField(blank=True)
    role_en = models.CharField(max_length=160, blank=True)
    role_ru = models.CharField(max_length=160, blank=True)
    year = models.CharField(max_length=20, blank=True)
    cover_image_url = models.URLField(blank=True)
    cover_alt_en = models.CharField(max_length=180, blank=True)
    cover_alt_ru = models.CharField(max_length=180, blank=True)
    video_url = models.URLField(blank=True)
    tags = models.JSONField(default=list)  # ["Django", "FastAPI", ...]
    highlights = models.JSONField(default=list, blank=True)
    links = models.JSONField(
        default=list
    )  # [{"type":"github","href":"...","label":{"en":"...","ru":"..."}}]
    order = models.PositiveIntegerField(default=0)
    source_prompt = models.TextField(blank=True)
    ai_notes = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["order", "slug"]

    def __str__(self):
        return self.slug

    def publish(self):
        self.status = self.Status.PUBLISHED
        self.published_at = self.published_at or timezone.now()
        self.save(update_fields=["status", "published_at", "updated_at"])


class ProjectMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        GIF = "gif", "GIF"

    project = models.ForeignKey(Project, related_name="media", on_delete=models.CASCADE)
    media_type = models.CharField(
        max_length=20, choices=MediaType.choices, default=MediaType.IMAGE
    )
    title_en = models.CharField(max_length=160, blank=True)
    title_ru = models.CharField(max_length=160, blank=True)
    url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    caption_en = models.CharField(max_length=240, blank=True)
    caption_ru = models.CharField(max_length=240, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title_en or self.title_ru or self.url


class ProjectDraft(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    target_project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        related_name="drafts",
        on_delete=models.SET_NULL,
    )
    ai_config = models.ForeignKey(
        "AIProviderConfig",
        null=True,
        blank=True,
        related_name="project_drafts",
        on_delete=models.SET_NULL,
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    slug = models.SlugField(max_length=80, blank=True)
    prompt = models.TextField(help_text="Raw project notes for AI generation.")
    context = models.TextField(
        blank=True, help_text="Extra tone, audience, constraints, or links."
    )
    title_en = models.CharField(max_length=200, blank=True)
    title_ru = models.CharField(max_length=200, blank=True)
    meta_en = models.CharField(max_length=80, blank=True)
    meta_ru = models.CharField(max_length=80, blank=True)
    summary_en = models.TextField(blank=True)
    summary_ru = models.TextField(blank=True)
    detail_en = models.TextField(blank=True)
    detail_ru = models.TextField(blank=True)
    problem_en = models.TextField(blank=True)
    problem_ru = models.TextField(blank=True)
    solution_en = models.TextField(blank=True)
    solution_ru = models.TextField(blank=True)
    result_en = models.TextField(blank=True)
    result_ru = models.TextField(blank=True)
    role_en = models.CharField(max_length=160, blank=True)
    role_ru = models.CharField(max_length=160, blank=True)
    year = models.CharField(max_length=20, blank=True)
    cover_image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    links = models.JSONField(default=list, blank=True)
    ai_model = models.CharField(max_length=80, blank=True)
    ai_response = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    published_project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        related_name="published_from_drafts",
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return self.title_ru or self.title_en or self.slug or f"Draft #{self.pk}"

    def publish_to_project(self):
        project = self.target_project or self.published_project
        if project is None:
            project = Project()

        project.slug = self.slug or project.slug
        project.status = Project.Status.PUBLISHED
        project.featured = True
        project.meta_en = self.meta_en
        project.meta_ru = self.meta_ru
        project.title_en = self.title_en
        project.title_ru = self.title_ru
        project.description_en = self.summary_en
        project.description_ru = self.summary_ru
        project.detail_en = self.detail_en
        project.detail_ru = self.detail_ru
        project.problem_en = self.problem_en
        project.problem_ru = self.problem_ru
        project.solution_en = self.solution_en
        project.solution_ru = self.solution_ru
        project.result_en = self.result_en
        project.result_ru = self.result_ru
        project.role_en = self.role_en
        project.role_ru = self.role_ru
        project.year = self.year
        project.cover_image_url = self.cover_image_url
        project.video_url = self.video_url
        project.tags = self.tags or []
        project.links = self.links or []
        project.source_prompt = self.prompt
        project.ai_notes = self.context
        project.published_at = project.published_at or timezone.now()
        project.save()

        self.status = self.Status.PUBLISHED
        self.published_project = project
        self.target_project = project
        self.save(
            update_fields=[
                "status",
                "published_project",
                "target_project",
                "updated_at",
            ]
        )
        return project


class TelegramPostDraft(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY = "ready", "Ready"
        SENT = "sent", "Sent"
        ARCHIVED = "archived", "Archived"

    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        related_name="telegram_drafts",
        on_delete=models.SET_NULL,
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    title = models.CharField(max_length=180)
    body = models.TextField()
    channel_hint = models.CharField(max_length=120, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return self.title


class AIProviderConfig(models.Model):
    class Provider(models.TextChoices):
        OPENAI = "openai", "OpenAI"
        OPENROUTER = "openrouter", "OpenRouter"

    class ModelChoice(models.TextChoices):
        OPENAI_GPT_4O_MINI = "gpt-4o-mini", "OpenAI: GPT-4o mini"
        OPENAI_GPT_4_1_NANO = "gpt-4.1-nano", "OpenAI: GPT-4.1 nano"
        OPENAI_GPT_4_1_MINI = "gpt-4.1-mini", "OpenAI: GPT-4.1 mini"
        OPENROUTER_LLAMA_FREE = (
            "meta-llama/llama-3.3-70b-instruct:free",
            "OpenRouter: Llama 3.3 70B free",
        )
        OPENROUTER_DEEPSEEK_FREE = (
            "deepseek/deepseek-chat-v3-0324:free",
            "OpenRouter: DeepSeek Chat free",
        )
        OPENROUTER_QWEN_FREE = (
            "qwen/qwen3-235b-a22b:free",
            "OpenRouter: Qwen3 235B free",
        )

    name = models.CharField(max_length=120)
    provider = models.CharField(
        max_length=24, choices=Provider.choices, default=Provider.OPENAI
    )
    model = models.CharField(
        max_length=120,
        choices=ModelChoice.choices,
        default=ModelChoice.OPENAI_GPT_4O_MINI,
    )
    custom_model = models.CharField(
        max_length=160,
        blank=True,
        help_text="Optional override if the model is not in the dropdown.",
    )
    api_key = models.CharField(max_length=255, blank=True)
    base_url = models.URLField(blank=True)
    is_enabled = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-is_default", "name"]

    def __str__(self):
        return f"{self.name} ({self.effective_model})"

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
        if self.is_default:
            type(self).objects.exclude(pk=self.pk).update(is_default=False)

    @property
    def masked_key(self):
        if not self.api_key:
            return ""
        if len(self.api_key) <= 10:
            return "***"
        return f"{self.api_key[:7]}...{self.api_key[-4:]}"

    @property
    def effective_model(self):
        return self.custom_model.strip() or self.model

    @classmethod
    def get_default(cls):
        return (
            cls.objects.filter(is_enabled=True, is_default=True).first()
            or cls.objects.filter(is_enabled=True).first()
        )


class VisitLog(models.Model):
    """Логи визитов для простой аналитики."""

    path = models.CharField(max_length=255)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Запись визита"
        verbose_name_plural = "Записи визитов"

    def __str__(self):
        return f"{self.ip} {self.path} {self.created_at}"

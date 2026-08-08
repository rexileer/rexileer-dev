from django.contrib import admin, messages
from django.db.models import Count, QuerySet
from django.db.models.functions import TruncDate
from django.http import HttpRequest
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    AIProviderConfig,
    Project,
    ProjectDraft,
    ProjectMedia,
    SiteText,
    Skill,
    TelegramPostDraft,
    VisitLog,
)
from .services.ai_portfolio import generate_portfolio_draft


class ProjectMediaInline(TabularInline):
    model = ProjectMedia
    extra = 1
    tab = True
    fields = (
        "order",
        "media_type",
        "title_ru",
        "title_en",
        "url",
        "thumbnail_url",
        "caption_ru",
        "caption_en",
    )


@admin.register(SiteText)
class SiteTextAdmin(ModelAdmin):
    list_display = ("key", "lang", "value_preview")
    list_filter = ("lang",)
    search_fields = ("key", "value")

    def value_preview(self, obj):
        return (obj.value[:60] + "...") if len(obj.value) > 60 else obj.value

    value_preview.short_description = "Value"


@admin.register(Skill)
class SkillAdmin(ModelAdmin):
    list_display = ("text", "lang", "order")
    list_filter = ("lang",)
    list_editable = ("order",)
    ordering = ("lang", "order")


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = (
        "title_ru",
        "slug",
        "status",
        "featured",
        "project_state",
        "client",
        "year",
        "order",
        "updated_at",
    )
    list_filter = ("status", "featured", "source_group", "project_state", "year")
    list_editable = ("status", "featured", "order")
    search_fields = ("slug", "title_en", "title_ru", "description_ru", "detail_ru")
    prepopulated_fields = {"slug": ("title_en",)}
    inlines = [ProjectMediaInline]
    actions = ["publish_projects", "archive_projects"]
    fieldsets = (
        (
            "Publication",
            {
                "fields": (
                    "status",
                    "featured",
                    "order",
                    "published_at",
                    "slug",
                    "year",
                    "source_group",
                    "client",
                    "project_state",
                )
            },
        ),
        (
            "Card copy",
            {
                "fields": (
                    ("meta_ru", "meta_en"),
                    ("title_ru", "title_en"),
                    "description_ru",
                    "description_en",
                    "tags",
                    "highlights",
                    "links",
                )
            },
        ),
        (
            "Project page",
            {
                "fields": (
                    "detail_ru",
                    "detail_en",
                    "problem_ru",
                    "problem_en",
                    "solution_ru",
                    "solution_en",
                    "result_ru",
                    "result_en",
                    ("role_ru", "role_en"),
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "cover_image_url",
                    ("cover_alt_ru", "cover_alt_en"),
                    "video_url",
                )
            },
        ),
        (
            "AI context",
            {"classes": ("collapse",), "fields": ("source_prompt", "ai_notes")},
        ),
    )
    readonly_fields = ("created_at", "updated_at")

    @admin.action(description="Publish selected projects")
    def publish_projects(self, request: HttpRequest, queryset: QuerySet):
        for project in queryset:
            project.publish()
        self.message_user(request, f"Published {queryset.count()} project(s).")

    @admin.action(description="Archive selected projects")
    def archive_projects(self, request: HttpRequest, queryset: QuerySet):
        updated = queryset.update(status=Project.Status.ARCHIVED)
        self.message_user(request, f"Archived {updated} project(s).")


@admin.register(ProjectDraft)
class ProjectDraftAdmin(ModelAdmin):
    list_display = (
        "__str__",
        "status",
        "slug",
        "target_project",
        "ai_config",
        "ai_model",
        "generated_at",
        "updated_at",
    )
    list_filter = ("status", "ai_model", "generated_at")
    search_fields = ("slug", "title_ru", "title_en", "prompt", "context")
    actions = ["generate_with_ai", "publish_drafts"]
    fieldsets = (
        (
            "Input",
            {
                "fields": (
                    "status",
                    "target_project",
                    "ai_config",
                    "slug",
                    "prompt",
                    "context",
                )
            },
        ),
        (
            "Generated card copy",
            {
                "fields": (
                    ("meta_ru", "meta_en"),
                    ("title_ru", "title_en"),
                    "summary_ru",
                    "summary_en",
                    "tags",
                    "links",
                )
            },
        ),
        (
            "Generated detail page",
            {
                "fields": (
                    "detail_ru",
                    "detail_en",
                    "problem_ru",
                    "problem_en",
                    "solution_ru",
                    "solution_en",
                    "result_ru",
                    "result_en",
                    ("role_ru", "role_en"),
                    "year",
                )
            },
        ),
        ("Media", {"fields": ("cover_image_url", "video_url")}),
        (
            "AI response",
            {
                "classes": ("collapse",),
                "fields": ("ai_model", "generated_at", "ai_response"),
            },
        ),
        (
            "Publication",
            {
                "classes": ("collapse",),
                "fields": ("published_project", "created_at", "updated_at"),
            },
        ),
    )
    readonly_fields = (
        "ai_model",
        "ai_response",
        "generated_at",
        "published_project",
        "created_at",
        "updated_at",
    )

    @admin.action(description="Generate portfolio copy with AI")
    def generate_with_ai(self, request: HttpRequest, queryset: QuerySet):
        generated = 0
        for draft in queryset:
            try:
                generate_portfolio_draft(draft)
            except Exception as exc:
                self.message_user(
                    request,
                    f"Draft #{draft.pk}: generation failed: {exc}",
                    level=messages.ERROR,
                )
            else:
                generated += 1
        if generated:
            self.message_user(request, f"Generated {generated} draft(s).")

    @admin.action(description="Publish selected drafts")
    def publish_drafts(self, request: HttpRequest, queryset: QuerySet):
        published = 0
        for draft in queryset:
            if not draft.slug:
                self.message_user(
                    request,
                    f"Draft #{draft.pk}: slug is required before publishing.",
                    level=messages.ERROR,
                )
                continue
            draft.publish_to_project()
            published += 1
        if published:
            self.message_user(request, f"Published {published} draft(s).")


@admin.register(TelegramPostDraft)
class TelegramPostDraftAdmin(ModelAdmin):
    list_display = ("title", "status", "project", "channel_hint", "scheduled_for")
    list_filter = ("status", "channel_hint", "scheduled_for")
    search_fields = ("title", "body", "channel_hint", "project__title_ru")
    autocomplete_fields = ("project",)
    fieldsets = (
        ("Draft", {"fields": ("status", "project", "title", "body")}),
        ("Telegram", {"fields": ("channel_hint", "scheduled_for")}),
    )


@admin.register(AIProviderConfig)
class AIProviderConfigAdmin(ModelAdmin):
    list_display = (
        "name",
        "provider",
        "model",
        "custom_model",
        "is_enabled",
        "is_default",
        "masked_key_display",
        "updated_at",
    )
    list_filter = ("provider", "is_enabled", "is_default")
    search_fields = ("name", "model", "base_url", "notes")
    list_editable = ("is_enabled", "is_default")
    fieldsets = (
        (
            "Provider",
            {
                "fields": (
                    "name",
                    "provider",
                    "model",
                    "custom_model",
                    "api_key",
                    "base_url",
                    "is_enabled",
                    "is_default",
                )
            },
        ),
        ("Notes", {"fields": ("notes",)}),
    )
    readonly_fields = ("created_at", "updated_at")

    def masked_key_display(self, obj):
        return obj.masked_key or "not set"

    masked_key_display.short_description = "API key"


@admin.register(VisitLog)
class VisitAnalyticsAdmin(ModelAdmin):
    change_list_template = "admin/visit_analytics.html"
    date_hierarchy = "created_at"
    list_display = ("created_at", "path", "ip", "user_agent")
    readonly_fields = ("created_at", "path", "ip", "user_agent")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if request.method in ("GET", "HEAD"):
            return True
        return False

    def changelist_view(self, request, extra_context=None):
        qs = VisitLog.objects.all()
        daily_stats = (
            qs.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(
                visits=Count("id"),
                unique_ips=Count("ip", distinct=True),
            )
            .order_by("-day")
        )

        extra_context = extra_context or {}
        extra_context["daily_stats"] = daily_stats

        return super().changelist_view(request, extra_context=extra_context)

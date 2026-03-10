from django.contrib import admin
from django.db.models import Count, DateField
from django.db.models.functions import TruncDate

from .models import SiteText, Skill, Project, VisitLog


@admin.register(SiteText)
class SiteTextAdmin(admin.ModelAdmin):
    list_display = ("key", "lang", "value_preview")
    list_filter = ("lang",)
    search_fields = ("key", "value")

    def value_preview(self, obj):
        return (obj.value[:60] + "…") if len(obj.value) > 60 else obj.value
    value_preview.short_description = "Value"


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("text", "lang", "order")
    list_filter = ("lang",)
    list_editable = ("order",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("slug", "title_en", "title_ru", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("title_en",)}


@admin.register(VisitLog)
class VisitAnalyticsAdmin(admin.ModelAdmin):
    """
    Панель аналитики: агрегированные визиты по дням и уникальным IP.
    """

    change_list_template = "admin/visit_analytics.html"
    date_hierarchy = "created_at"
    list_display = ("created_at", "path", "ip", "user_agent")
    readonly_fields = ("created_at", "path", "ip", "user_agent")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Разрешаем только просмотр (чтобы открыть панель)
        if request.method in ("GET", "HEAD"):
            return True
        return False

    def changelist_view(self, request, extra_context=None):
        # Агрегация по датам: всего визитов и уникальных IP
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

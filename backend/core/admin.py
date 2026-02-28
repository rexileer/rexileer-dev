from django.contrib import admin
from .models import SiteText, Skill, Project


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

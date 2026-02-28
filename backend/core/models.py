from django.db import models


class SiteText(models.Model):
    """Тексты сайта по ключам (data-i18n). key например: hero.title, contact.labels.email"""
    key = models.CharField(max_length=120, db_index=True)
    lang = models.CharField(max_length=5, choices=[("en", "English"), ("ru", "Русский")])
    value = models.TextField(blank=True)

    class Meta:
        unique_together = [("key", "lang")]
        ordering = ["key", "lang"]

    def __str__(self):
        return f"{self.key} ({self.lang})"


class Skill(models.Model):
    lang = models.CharField(max_length=5, choices=[("en", "English"), ("ru", "Русский")])
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["lang", "order"]

    def __str__(self):
        return f"{self.text} ({self.lang})"


class Project(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    meta_en = models.CharField(max_length=80, blank=True)
    meta_ru = models.CharField(max_length=80, blank=True)
    title_en = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)
    description_en = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    tags = models.JSONField(default=list)  # ["Django", "FastAPI", ...]
    links = models.JSONField(default=list)  # [{"type":"github","href":"...","label":{"en":"...","ru":"..."}}]
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "slug"]

    def __str__(self):
        return self.slug

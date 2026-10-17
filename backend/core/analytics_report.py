from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from .models import SiteEvent, VisitLog


def acquisition_report(days=7, is_test=False):
    cutoff = timezone.now() - timedelta(days=days)
    scope = {"created_at__gte": cutoff, "is_test": is_test, "version": 1}
    views = VisitLog.objects.filter(**scope)
    events = SiteEvent.objects.filter(**scope)
    totals = {
        "views": views.count(),
        "entries": views.filter(is_entry=True).count(),
        "telegram": events.filter(name="telegram_click").count(),
        "email": events.filter(name="email_click").count(),
        "cases": events.filter(name="case_open").count(),
    }
    source_fields = ("utm_source", "utm_medium", "utm_campaign", "referrer_domain")
    sources = {}
    for row in views.values(*source_fields).annotate(
        views=Count("id"), entries=Count("id", filter=Q(is_entry=True))
    ):
        key = tuple(row[k] for k in source_fields)
        sources[key] = {**row, "telegram": 0, "email": 0}
    for row in events.values(*source_fields).annotate(
        telegram=Count("id", filter=Q(name="telegram_click")),
        email=Count("id", filter=Q(name="email_click")),
    ):
        key = tuple(row[k] for k in source_fields)
        sources.setdefault(
            key, {**dict(zip(source_fields, key)), "views": 0, "entries": 0}
        )
        sources[key].update(telegram=row["telegram"], email=row["email"])

    def popular(queryset):
        return (
            queryset.values("path")
            .annotate(total=Count("id"))
            .order_by("-total", "path")[:30]
        )

    return {
        "days": days,
        "is_test": is_test,
        "cutoff": cutoff,
        "totals": totals,
        "sample_small": totals["views"] < 30,
        "sources": sorted(
            sources.values(), key=lambda r: (-r["views"], -r["telegram"], -r["email"])
        )[:30],
        "entries": popular(views.filter(is_entry=True)),
        "services": popular(
            views.filter(
                Q(path__startswith="/services/") | Q(path__startswith="/en/services/")
            ).exclude(path__in=("/services/", "/en/services/"))
        ),
        "cases": popular(
            views.filter(
                Q(path__startswith="/projects/") | Q(path__startswith="/en/projects/")
            ).exclude(path__in=("/projects/", "/en/projects/"))
        ),
        "contact_pages": events.filter(name__in=("telegram_click", "email_click"))
        .values("path")
        .annotate(
            telegram=Count("id", filter=Q(name="telegram_click")),
            email=Count("id", filter=Q(name="email_click")),
        )
        .order_by("-telegram", "-email", "path")[:30],
        "legacy_views": VisitLog.objects.filter(
            created_at__gte=cutoff, version=0
        ).count(),
        "legacy_events": SiteEvent.objects.filter(
            created_at__gte=cutoff, version=0
        ).count(),
    }

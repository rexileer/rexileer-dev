from datetime import timedelta

from core.models import SiteEvent, VisitLog
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Delete only page/click analytics rows older than 90 days."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=90)
        for model in (SiteEvent, VisitLog):
            count = 0
            while ids := list(
                model.objects.filter(created_at__lt=cutoff).values_list(
                    "pk", flat=True
                )[:500]
            ):
                deleted, _ = model.objects.filter(pk__in=ids).delete()
                count += deleted
            self.stdout.write(
                f"{model.__name__}: removed {count} rows older than 90 days"
            )

import logging

from django.http import HttpResponseNotFound
from django.utils.deprecation import MiddlewareMixin

from .analytics import record_view

logger = logging.getLogger(__name__)

SUSPICIOUS_PATH_PREFIXES = (
    "/.env",
    "/.git",
    "/actuator",
    "/cgi-bin",
    "/phpmyadmin",
    "/server-status",
    "/vendor",
    "/wp-",
    "/xmlrpc.php",
)


class VisitLoggingMiddleware(MiddlewareMixin):
    """Count successful public HTML responses without affecting navigation."""

    def process_request(self, request):
        normalized = request.path.lower()
        if any(
            normalized == prefix or normalized.startswith(f"{prefix}/")
            for prefix in SUSPICIOUS_PATH_PREFIXES
        ):
            return HttpResponseNotFound()

    def process_response(self, request, response):
        try:
            record_view(request, response)
        except Exception:
            # No request payload, URL query, IP or UA in operational error messages.
            logger.warning("Page analytics unavailable")
        return response

from datetime import timedelta
from ipaddress import ip_address

from django.http import HttpResponseNotFound
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from .models import VisitLog

SCANNER_USER_AGENT_TOKENS = (
    "ahrefs",
    "banner detection",
    "bot",
    "bytespider",
    "censys",
    "claudebot",
    "crawler",
    "curl",
    "expanse",
    "go-http-client",
    "gptbot",
    "httpx",
    "internetmeasurement",
    "masscan",
    "nikto",
    "palo alto",
    "python-requests",
    "python-urllib",
    "scanner",
    "semrush",
    "spider",
    "visionheight",
    "wget",
    "zgrab",
)
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
VISIT_DEDUPE_WINDOW = timedelta(hours=6)


class VisitLoggingMiddleware(MiddlewareMixin):
    """Log lightweight homepage analytics while ignoring common scanners."""

    def process_request(self, request):
        if self._is_suspicious_path(request.path):
            return HttpResponseNotFound()

        if request.method != "GET":
            return
        if request.path != "/":
            return

        user_agent = request.META.get("HTTP_USER_AGENT", "").strip()
        if self._is_scanner_user_agent(user_agent):
            return

        client_ip = self._client_ip(request)
        if self._was_recently_logged(client_ip, user_agent):
            return

        VisitLog.objects.create(
            path=request.path,
            ip=client_ip,
            user_agent=user_agent[:1000],
        )

    @staticmethod
    def _client_ip(request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        raw_ip = xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")
        if not raw_ip:
            return None

        try:
            return str(ip_address(raw_ip))
        except ValueError:
            return None

    @staticmethod
    def _is_scanner_user_agent(user_agent):
        if not user_agent:
            return True
        normalized = user_agent.lower()
        return any(token in normalized for token in SCANNER_USER_AGENT_TOKENS)

    @staticmethod
    def _is_suspicious_path(path):
        normalized = path.lower()
        return any(
            normalized == prefix or normalized.startswith(f"{prefix}/")
            for prefix in SUSPICIOUS_PATH_PREFIXES
        )

    @staticmethod
    def _was_recently_logged(client_ip, user_agent):
        cutoff = timezone.now() - VISIT_DEDUPE_WINDOW
        return VisitLog.objects.filter(
            ip=client_ip,
            user_agent=user_agent[:1000],
            created_at__gte=cutoff,
        ).exists()

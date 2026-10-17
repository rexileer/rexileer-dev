"""Small first-party counters, bounded attribution and shared traffic filtering."""

import logging
import re
import secrets
from datetime import timedelta
from functools import lru_cache
from ipaddress import ip_address
from urllib.parse import urlsplit

from django.conf import settings
from django.core import signing
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .content import SERVICES
from .models import AnalyticsKey, Project, SiteEvent, VisitLog

logger = logging.getLogger(__name__)
COOKIE = "rex_attribution"
COOKIE_SALT = "rexileer.analytics.v1"
ATTRIBUTION_SECONDS = 1800
VIEW_LIMIT = 60
EVENT_LIMIT = 30
UTM_FIELDS = ("utm_source", "utm_medium", "utm_campaign")
SCANNER_TOKENS = (
    "bot",
    "crawler",
    "spider",
    "scanner",
    "curl",
    "wget",
    "python",
    "httpx",
    "headless",
    "playwright",
    "rexileer-qa",
    "censys",
    "expanse",
    "masscan",
    "nikto",
    "zgrab",
    "go-http-client",
    "internetmeasurement",
    "palo alto",
    "banner detection",
    "visionheight",
    "ahrefs",
    "semrush",
)


@lru_cache(maxsize=1)
def analytics_key():
    # Retained in the existing private DB; never shown in the admin or public API.
    state, _ = AnalyticsKey.objects.get_or_create(
        pk=1, defaults={"key": secrets.token_hex(32)}
    )
    return state.key


def public_path(path):
    if not isinstance(path, str) or len(path) > 255:
        return False
    base = path[3:] if path.startswith("/en/") else path
    if base in {"/", "/services/", "/projects/", "/work/", "/privacy/"}:
        return True
    if base in {f"/services/{s['slug']}/" for s in SERVICES}:
        return True
    match = re.fullmatch(r"/projects/([a-z0-9-]+)/", base)
    return bool(
        match
        and Project.objects.filter(
            slug=match[1], status=Project.Status.PUBLISHED
        ).exists()
    )


def client_ip(request):
    raw = request.META.get("REMOTE_ADDR", "")
    try:
        peer = ip_address(raw)
        # The app is loopback-only behind nginx, which overwrites X-Real-IP.
        if peer.is_private or peer.is_loopback:
            raw = request.META.get("HTTP_X_REAL_IP") or raw
        return str(ip_address(raw))
    except ValueError:
        return ""


def client_key(request):
    # A daily HMAC of IP for abuse limiting only; never a person/session metric.
    value = f"{timezone.now().date().isoformat()}|{client_ip(request)}"
    return salted_hmac(
        "rexileer.analytics.rate.v1", value, secret=analytics_key(), algorithm="sha256"
    ).hexdigest()


def cookie_context(request):
    try:
        value = signing.loads(
            request.COOKIES.get(COOKIE, ""),
            key=analytics_key(),
            fallback_keys=[],
            salt=COOKIE_SALT,
            max_age=ATTRIBUTION_SECONDS,
        )
        if isinstance(value, dict) and public_path(value.get("entry_path")):
            return value
    except (signing.BadSignature, ValueError, TypeError):
        pass
    return {}


def test_traffic(request, context):
    return (
        request.headers.get("X-Rexileer-Analytics") == "test"
        or context.get("is_test") is True
    )


def excluded(request, context):
    if request.headers.get("DNT") == "1" or request.headers.get("Sec-GPC") == "1":
        return True
    if request.headers.get("X-Rexileer-Analytics") == "exclude":
        return True
    if test_traffic(request, context):
        return False
    user = getattr(request, "user", None)
    if user and user.is_authenticated and user.is_staff:
        return True
    if client_ip(request) in getattr(settings, "ANALYTICS_EXCLUDED_IPS", ()):
        return True
    agent = request.META.get("HTTP_USER_AGENT", "").lower()
    return not agent or any(token in agent for token in SCANNER_TOKENS)


def utm_value(value, limit=64):
    # Whole value rejected, never truncate a URL/email/free-form string into a slug.
    if isinstance(value, str) and re.fullmatch(
        r"[a-zA-Z][a-zA-Z0-9_-]{0," + str(limit - 1) + r"}", value
    ):
        return value.lower()
    return ""


def referrer_domain(request):
    raw = request.META.get("HTTP_REFERER", "")
    if len(raw) > 2048:
        return ""
    try:
        url = urlsplit(raw)
        host = (
            (url.hostname or "")
            .encode("idna")
            .decode("ascii")
            .lower()
            .removeprefix("www.")
        )
        if url.scheme not in {"http", "https"} or len(host) > 253:
            return ""
        if host == "rexileer.ru" or host.endswith(".rexileer.ru"):
            return ""
        if host == request.get_host().split(":")[0].removeprefix("www."):
            return ""
        if not re.fullmatch(
            r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{1,62}", host
        ):
            return ""
        return host
    except (ValueError, UnicodeError):
        return ""


def attribution(request, previous):
    tags = {
        field: utm_value(request.GET.get(field), 32 if field == "utm_medium" else 64)
        for field in UTM_FIELDS
    }
    domain = referrer_domain(request)
    is_test = test_traffic(request, previous)
    # A newly tagged/external arrival starts a fresh fixed 30-minute chain.
    tagged_change = any(tags.values()) and any(
        tags[k] != previous.get(k, "") for k in UTM_FIELDS
    )
    fresh = (
        not previous
        or tagged_change
        or bool(domain)
        or previous.get("is_test") != is_test
    )
    if fresh:
        return {
            **tags,
            "referrer_domain": domain,
            "entry_path": request.path,
            "is_test": is_test,
        }, True
    return previous, False


def fields(context):
    return {
        key: context.get(key, "")
        for key in (*UTM_FIELDS, "referrer_domain", "entry_path")
    }


def limited(model, key, is_test, limit):
    return (
        model.objects.filter(
            client_key=key,
            is_test=is_test,
            created_at__gte=timezone.now() - timedelta(minutes=1),
        ).count()
        >= limit
    )


def record_view(request, response):
    if request.method != "GET" or response.status_code != 200:
        return
    if not response.get("Content-Type", "").startswith("text/html"):
        return
    if not public_path(request.path):
        return
    previous = cookie_context(request)
    if excluded(request, previous):
        return
    context, is_entry = attribution(request, previous)
    key = client_key(request)
    if limited(VisitLog, key, context["is_test"], VIEW_LIMIT):
        return
    VisitLog.objects.create(
        path=request.path,
        client_key=key,
        version=1,
        is_test=context["is_test"],
        is_entry=is_entry,
        **fields(context),
    )
    if is_entry:
        response.set_cookie(
            COOKIE,
            signing.dumps(
                context, key=analytics_key(), salt=COOKIE_SALT, compress=True
            ),
            max_age=ATTRIBUTION_SECONDS,
            httponly=True,
            secure=request.is_secure(),
            samesite="Lax",
        )


def record_event(request, name, location, path, lang):
    context = cookie_context(request)
    if excluded(request, context):
        return
    key = client_key(request)
    is_test = test_traffic(request, context)
    if limited(SiteEvent, key, is_test, EVENT_LIMIT):
        return
    if SiteEvent.objects.filter(
        client_key=key,
        is_test=is_test,
        name=name,
        location=location,
        path=path,
        created_at__gte=timezone.now() - timedelta(seconds=2),
    ).exists():
        return
    SiteEvent.objects.create(
        name=name,
        location=location,
        path=path,
        lang=lang,
        client_key=key,
        is_test=is_test,
        version=1,
        **fields(context),
    )

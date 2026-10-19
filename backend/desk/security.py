from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .models import LoginGuard


def is_owner(user):
    return (
        user.is_authenticated
        and user.is_active
        and user.is_superuser
        and user.username == settings.OWNER_USERNAME
    )


class PrivateHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = (
            request.get_host()
        )  # Validate before sessions, CSRF or health exceptions.
        origin = request.headers.get("Origin")
        expected = f"{'https' if request.is_secure() else 'http'}://{host}"
        response = (
            HttpResponse("Источник запроса отклонён.", status=403)
            if origin and origin != expected
            else self.get_response(request)
        )
        response["Cache-Control"] = "no-store, private, max-age=0"
        response["Pragma"] = "no-cache"
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        response["Cross-Origin-Resource-Policy"] = "same-origin"
        response.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'none'; style-src 'self'; font-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
        )
        return response


class OwnerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public = request.path in ("/login/", "/robots.txt") or request.path.startswith(
            "/assets/"
        )
        health = request.path == "/health/" and request.META.get("REMOTE_ADDR") in (
            "127.0.0.1",
            "::1",
        )
        if not public and not health and not is_owner(request.user):
            if request.user.is_authenticated:
                return HttpResponse("Доступ только владельцу.", status=403)
            # Do not place searches or personal form data in a redirect URL.
            return HttpResponseRedirect("/login/")
        return self.get_response(request)


def safe_next(request):
    target = request.POST.get("next", request.GET.get("next", "/"))
    return (
        target
        if url_has_allowed_host_and_scheme(
            target, {request.get_host()}, require_https=request.is_secure()
        )
        else "/"
    )


@transaction.atomic
def reserve_login():
    from .services import workspace_lock

    workspace_lock()
    now = timezone.now()
    LoginGuard.objects.get_or_create(pk=1, defaults={"window": now})
    # Acquire SQLite's write lock before reading the shared allowance.
    LoginGuard.objects.filter(pk=1).update(attempts=F("attempts") + 1)
    guard = LoginGuard.objects.get(pk=1)
    if guard.blocked_until and guard.blocked_until > now:
        return False
    if guard.window < now - timedelta(minutes=15):
        guard.window, guard.attempts, guard.blocked_until = now, 1, None
    allowed = guard.attempts <= 8
    if not allowed:
        guard.blocked_until = now + timedelta(minutes=15)
    guard.save()
    return allowed


def reset_login_guard():
    LoginGuard.objects.filter(pk=1).update(
        attempts=0, window=timezone.now(), blocked_until=None
    )

from django.utils.deprecation import MiddlewareMixin

from .models import VisitLog


class VisitLoggingMiddleware(MiddlewareMixin):
    """
    Простое логирование визитов.
    Сейчас считаем визитом только открытие главной страницы ("/").
    """

    def process_request(self, request):
        if request.method != "GET":
            return
        if request.path != "/":
            return

        # IP-адрес: сперва X-Forwarded-For (если за nginx), потом REMOTE_ADDR
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            ip = xff.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")

        ua = request.META.get("HTTP_USER_AGENT", "")

        VisitLog.objects.create(path=request.path, ip=ip, user_agent=ua)


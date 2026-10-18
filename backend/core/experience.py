"""Presentation-only walkthroughs grounded in existing case workflows."""

from .content import pair

SCENARIOS = [
    {
        "id": "access",
        "label": pair("Оплата и доступ", "Payment & access"),
        "input": pair(
            "Пользователь оформляет подписку в Telegram",
            "A user subscribes through Telegram",
        ),
        "output": pair("Оплата связана с доступом.", "Payment becomes access."),
        "result": pair(
            "Персональный инвайт, срок подписки и уведомления — в одном процессе.",
            "A personal invite, subscription period and notifications in one workflow.",
        ),
        "project": "payment-broadcast-bot",
        "steps": [
            {
                "title": pair("Подтверждение", "Confirmation"),
                "detail": pair(
                    "Обработчик получает подтверждение платежа от YooKassa.",
                    "The handler receives payment confirmation from YooKassa.",
                ),
            },
            {
                "title": pair("Подписка", "Subscription"),
                "detail": pair(
                    "Backend сохраняет статус и срок доступа пользователя.",
                    "The backend stores the user's access status and expiry.",
                ),
            },
            {
                "title": pair("Приглашение", "Invitation"),
                "detail": pair(
                    "Бот выдаёт персональную invite-ссылку в закрытый канал.",
                    "The bot issues a personal invite to the private channel.",
                ),
            },
            {
                "title": pair("Проверка срока", "Expiry check"),
                "detail": pair(
                    "Фоновая проверка управляет напоминаниями и окончанием доступа.",
                    "Background checks handle reminders and access expiry.",
                ),
            },
        ],
    },
    {
        "id": "collection",
        "label": pair("Сбор данных", "Data collection"),
        "input": pair(
            "Приложение отправляет запрос на сбор",
            "An application requests a data collection job",
        ),
        "output": pair("Сбор работает в фоне.", "Collection runs in the background."),
        "result": pair(
            "Клиент получает статус и результат, не удерживая HTTP-соединение.",
            "The client gets the status and result without holding an HTTP connection open.",
        ),
        "project": "avito-parts-parser",
        "steps": [
            {
                "title": pair("Запрос API", "API request"),
                "detail": pair(
                    "FastAPI принимает параметры и создаёт задание.",
                    "FastAPI accepts the parameters and creates a job.",
                ),
            },
            {
                "title": pair("Очередь", "Queue"),
                "detail": pair(
                    "Redis и Celery отделяют приём запроса от тяжёлой обработки.",
                    "Redis and Celery separate request handling from heavy processing.",
                ),
            },
            {
                "title": pair("Сбор", "Collection"),
                "detail": pair(
                    "Изолированный worker запускает браузер и работает через прокси.",
                    "An isolated worker runs the browser through a proxy.",
                ),
            },
            {
                "title": pair("Результат", "Result"),
                "detail": pair(
                    "Статус задания и собранные данные доступны клиентскому приложению.",
                    "The job status and collected data are available to the client application.",
                ),
            },
        ],
    },
    {
        "id": "knowledge",
        "label": pair("Ответ по документам", "Document answers"),
        "input": pair(
            "Вопрос клиента поступает из Bitrix24",
            "A customer question arrives from Bitrix24",
        ),
        "output": pair(
            "Ответ опирается на знания.", "An answer grounded in knowledge."
        ),
        "result": pair(
            "Каталог и документы дают контекст для ответа в CRM.",
            "Catalog and document search provide the context for a CRM reply.",
        ),
        "project": "ai-consultant-bitrix-rag",
        "steps": [
            {
                "title": pair("Вопрос", "Question"),
                "detail": pair(
                    "Webhook передаёт сообщение из Bitrix24 в backend.",
                    "A webhook passes the Bitrix24 message to the backend.",
                ),
            },
            {
                "title": pair("Обработка", "Processing"),
                "detail": pair(
                    "Redis/RQ выполняет обработку, не заставляя CRM ждать вызова LLM.",
                    "Redis/RQ handles the work without making the CRM wait for the LLM call.",
                ),
            },
            {
                "title": pair("Поиск знаний", "Retrieval"),
                "detail": pair(
                    "Поиск по каталогу и документам собирает контекст для ответа.",
                    "Catalog and document search assembles the context for the reply.",
                ),
            },
            {
                "title": pair("Ответ в CRM", "CRM reply"),
                "detail": pair(
                    "Ответ готовится по найденному контексту и возвращается в диалог.",
                    "The reply is prepared from the retrieved context and returned to the conversation.",
                ),
            },
        ],
    },
]

FEATURED = {
    "meatbot-production-crm": {
        "headline": pair(
            "Цех и офис.\nОдин рабочий контур.",
            "Shop floor and office.\nOne working system.",
        ),
        "discipline": pair(
            "Производство / бизнес-система", "Production / business system"
        ),
        "work": pair(
            "Доменная модель, backend и рабочие сценарии офиса и цеха.",
            "The domain model, backend and office/shop-floor workflows.",
        ),
    },
    "avito-parts-parser": {
        "headline": pair(
            "Тяжёлая работа —\nза пределами запроса.",
            "Heavy processing.\nBeyond the request.",
        ),
        "discipline": pair(
            "Данные / фоновая обработка", "Data / background processing"
        ),
        "work": pair(
            "API, очереди и изолированные браузерные workers с прокси.",
            "The API, queues and isolated browser workers with proxies.",
        ),
    },
    "ai-consultant-bitrix-rag": {
        "headline": pair(
            "Не просто ответ.\nСвязь с вашими данными.",
            "More than an answer.\nConnected to your data.",
        ),
        "discipline": pair("AI / поиск / CRM", "AI / retrieval / CRM"),
        "work": pair(
            "Интеграция Bitrix24, поиск по знаниям и фоновая подготовка ответа.",
            "Bitrix24 integration, knowledge retrieval and background answer preparation.",
        ),
    },
}

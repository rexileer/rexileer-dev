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


LAB_COPY = {
    "run": pair("Запустить", "Run"),
    "pause": pair("Пауза", "Pause"),
    "resume": pair("Продолжить", "Resume"),
    "replay": pair("Повторить", "Run again"),
    "step": pair("Один шаг", "One step"),
    "reset": pair("Сбросить", "Reset"),
    "size": pair("Задач в наборе", "Tasks in batch"),
    "fault": pair("Сбой обработчика · один за запуск", "Worker failure · once per run"),
    "repair": pair("Восстановить обработчик", "Restore worker"),
    "ready": pair("Ещё не запущено", "Not started"),
    "running": pair("Идёт обработка", "Processing"),
    "paused": pair("Обработка на паузе", "Processing paused"),
    "blocked": pair("Обработчик остановлен", "Worker stopped"),
    "complete": pair("Набор готов", "Batch complete"),
    "total": pair("Всего", "Total"),
    "queued": pair("Ожидают", "Waiting"),
    "working": pair("В работе", "In progress"),
    "done": pair("Готовы", "Done"),
    "error": pair("Ошибка", "Error"),
    "request": pair("Запрос", "Request"),
    "queue": pair("Очередь", "Queue"),
    "worker": pair("Обработчик", "Worker"),
    "output": pair("Результат", "Result"),
    "modelSteps": pair("Шаги модели", "Model steps"),
    "tasks": pair("Задачи", "Tasks"),
    "chartData": pair("Числа по шагам", "Numbers by step"),
    "chartTitle": pair("Очередь и готовые результаты", "Queue and completed results"),
    "chartHint": pair(
        "Учебные шаги, не секунды и не скорость проекта.",
        "Model steps, not seconds or project performance.",
    ),
    "collectionHint": pair(
        "Измените набор или включите сбой: неполученный результат остаётся задачей, а повтор сохраняет её номер.",
        "Change the batch or inject a failure: unfinished work stays a task, and a retry keeps its identity.",
    ),
    "readyText": pair(
        "Набор в очереди. Запустите обработку или пройдите один шаг.",
        "The batch is queued. Start processing or advance one step.",
    ),
    "processingText": pair(
        "Одна задача перешла из очереди к обработчику.",
        "One task moved from the queue to the worker.",
    ),
    "deliveredText": pair(
        "Задача завершена: в результате появилась новая запись.",
        "A task finished: a new record appeared in the result.",
    ),
    "failureText": pair(
        "Текущая попытка остановлена. Восстановите обработчик, затем продолжите: результат не будет продублирован.",
        "This attempt stopped. Restore the worker, then resume: the output will not be duplicated.",
    ),
    "retryText": pair(
        "Та же задача вернулась в очередь. Нажмите «Продолжить».",
        "The same task returned to the queue. Select Resume.",
    ),
    "completeText": pair(
        "Все задачи завершены. Повторный запуск создаст новый учебный набор.",
        "All tasks are complete. Running again starts a new demo batch.",
    ),
    "record": pair("Запись", "Record"),
    "demoRecords": pair("Демонстрационные записи", "Sample records"),
    "emptyRecords": pair(
        "Готовые записи появятся после обработки.",
        "Completed records will appear after processing.",
    ),
    "moreRecords": pair(
        "Дополнительных готовых записей", "Additional completed records"
    ),
    "confirmed": pair("Платёж подтверждён", "Payment confirmed"),
    "term": pair("Срок подписки", "Subscription term"),
    "validTerm": pair("Действует", "Valid"),
    "expiredTerm": pair("Истёк", "Expired"),
    "accessHint": pair(
        "Подтверждение и срок меняют решение о доступе. Приглашение ниже — только визуальный пример.",
        "Confirmation and expiry change the access decision. The invitation below is a visual example only.",
    ),
    "pendingAccess": pair("Доступ ещё не проверен", "Access not checked yet"),
    "unconfirmed": pair("Нужно подтверждение оплаты", "Payment confirmation needed"),
    "active": pair("Доступ активен", "Access active"),
    "expired": pair("Срок доступа истёк", "Access expired"),
    "noInvite": pair("Приглашение не выдано", "No invitation issued"),
    "inactiveInvite": pair("Приглашение недействительно", "Invitation inactive"),
    "demoInvite": pair("Приглашение · DEMO-INVITE", "Invitation · DEMO-INVITE"),
    "demoChannel": pair("Демо · закрытый канал", "Demo · private channel"),
    "payment": pair("Платёж", "Payment"),
    "subscription": pair("Подписка", "Subscription"),
    "invitation": pair("Приглашение", "Invitation"),
    "notConfirmed": pair("Не подтверждён", "Unconfirmed"),
    "question": pair("Вопрос", "Question"),
    "source": pair("Справка подключена", "Reference connected"),
    "knowledgeHint": pair(
        "Выберите вопрос или отключите справку. Подсветка покажет, откуда берётся шаблонный ответ.",
        "Choose a question or disconnect the reference. The highlighted passage shows where the template answer comes from.",
    ),
    "questions": [
        pair("Как получить доступ?", "How do I get access?"),
        pair("Когда заканчивается подписка?", "When does the subscription end?"),
        pair("Какая гарантия возврата?", "What is the refund guarantee?"),
    ],
    "documents": [
        {
            "title": pair("Демо-документ: доступ", "Demo document: access"),
            "text": pair(
                "После подтверждения оплаты выдаётся приглашение в закрытый канал.",
                "Payment confirmation is followed by an invitation to the private channel.",
            ),
        },
        {
            "title": pair("Демо-документ: срок", "Demo document: term"),
            "text": pair(
                "Доступ действует до даты, указанной в подписке.",
                "Access lasts until the date specified in the subscription.",
            ),
        },
    ],
    "answer": pair("Ответ по справке", "Answer from the reference"),
    "pendingAnswer": pair(
        "Выберите вопрос и запустите поиск", "Choose a question and start retrieval"
    ),
    "insufficient": pair("Сведений недостаточно", "Insufficient context"),
    "insufficientText": pair(
        "В подключённой справке нет ответа. Нужен другой документ или уточнение.",
        "The connected reference has no answer. Another document or clarification is needed.",
    ),
    "found": pair("Найден фрагмент", "Passage found"),
    "search": pair("Поиск", "Retrieval"),
    "context": pair("Контекст", "Context"),
    "templateNote": pair(
        "Шаблонный ответ по синтетической справке.",
        "Template answer from a synthetic reference.",
    ),
    "demo": pair("Демонстрационные данные", "Demonstration data"),
}

"""Authored bilingual copy. Service claims are grounded in the project registry."""


def pair(ru, en):
    return {"ru": ru, "en": en}


def localize(value, lang):
    if isinstance(value, dict):
        if set(value) == {"ru", "en"}:
            return value[lang]
        return {key: localize(item, lang) for key, item in value.items()}
    if isinstance(value, list):
        return [localize(item, lang) for item in value]
    return value


UI = {
    "cases": pair("Проекты", "Projects"),
    "services": pair("Услуги", "Services"),
    "work": pair("Другие работы", "More work"),
    "contact": pair("Контакты", "Contact"),
    "discuss": pair("Обсудить задачу", "Discuss your project"),
    "telegram": pair("Обсудить задачу в Telegram", "Let's talk on Telegram"),
    "see_cases": pair("Посмотреть проекты", "Explore the projects"),
    "hero_title": pair("Backend, AI и автоматизация.", "Backend, AI & automation."),
    "hero_accent": pair("Чтобы всё работало.", "Built to work."),
    "hero_lead": pair(
        "Разрабатываю Python-сервисы, Telegram-ботов, парсеры и AI-интеграции. Подключаюсь к существующим проектам: разбираюсь в коде, исправляю проблемы и довожу систему до запуска.",
        "I build Python services, Telegram bots, data pipelines and AI integrations. I also take over existing projects: understand the code, fix what's broken and get the system running.",
    ),
    "pipeline_label": pair("От запроса — до результата", "From request to result"),
    "pipeline_note": pair(
        "Типовой контур системы. Архитектура подбирается под задачу.",
        "An example system flow. The architecture follows the problem.",
    ),
    "request": pair("Запрос / событие", "Request / event"),
    "rules": pair("API и бизнес-правила", "API & business rules"),
    "queue": pair("Фоновые задачи", "Background jobs"),
    "data": pair("Данные и поиск", "Data & retrieval"),
    "answer": pair("Интеграция / ответ", "Integration / response"),
    "direction_title": pair("С какой задачей прийти", "What can I help with?"),
    "direction_lead": pair(
        "От отдельной интеграции до backend-продукта. Выберите направление — там задачи, подход и реальные кейсы.",
        "From a single integration to a complete backend product. Each service explains the work, the approach and relevant projects.",
    ),
    "all_services": pair("Все услуги", "All services"),
    "selected": pair("Из практики", "Selected work"),
    "cases_title": pair(
        "Задача. Решение. Рабочий результат.", "Real problems. Working systems."
    ),
    "cases_lead": pair(
        "Интерфейсы, сценарии и архитектурные решения из реальных проектов. Без выдуманных отзывов и показателей.",
        "Actual interfaces, workflows and engineering decisions. Each case explains the problem, my contribution and the resulting system.",
    ),
    "all_cases": pair("Все кейсы", "All case studies"),
    "problem": pair("Задача", "Problem"),
    "solution": pair("Решение", "Solution"),
    "result": pair("Результат", "Outcome"),
    "role": pair("Мой вклад", "My contribution"),
    "stack": pair("Технологии", "Technology"),
    "read_case": pair("Разобрать кейс", "Read the case"),
    "rescue_eyebrow": pair("Не обязательно с нуля", "Existing projects welcome"),
    "rescue_title": pair("Проект уже существует?", "Already have a project?"),
    "rescue_lead": pair(
        "Бот сломался, API отдаёт ошибку или предыдущий разработчик ушёл — можно начать с текущего кода.",
        "A broken bot, a failing API, or a developer who moved on — we can start with what you already have.",
    ),
    "rescue_steps": pair(
        [
            "Изучу код и воспроизведу проблему",
            "Определю, что можно сохранить",
            "Исправлю критичные места",
            "Проверю и доведу до рабочего состояния",
        ],
        [
            "Read the code and reproduce the issue",
            "Identify what can be kept",
            "Fix the critical parts",
            "Verify the system and get it running",
        ],
    ),
    "audit": pair(
        "Если объём пока неясен, начнём с небольшого платного аудита. На выходе — причины проблем, приоритеты и следующий шаг.",
        "If the scope is unclear, we can start with a small paid diagnostic review. You get the causes, priorities and a practical next step.",
    ),
    "send_code": pair(
        "Прислать задачу или текущий код", "Send the task or existing code"
    ),
    "process_eyebrow": pair("Прозрачный процесс", "A clear process"),
    "process_title": pair(
        "Сначала разобраться. Потом разработать.", "Understand first. Build second."
    ),
    "process": [
        {
            "title": pair("Разбираемся в задаче", "Understand the problem"),
            "text": pair(
                "Обсуждаем сценарий, ограничения и текущую систему. Уточняем, какой результат нужен.",
                "We discuss the workflow, constraints and existing system, then define the result you need.",
            ),
        },
        {
            "title": pair("Фиксируем объём", "Agree the scope"),
            "text": pair(
                "Выбираем архитектуру, этапы и критерии готовности. Отдельно обозначаем неизвестные.",
                "We agree the approach, milestones and acceptance criteria, and make uncertainties explicit.",
            ),
        },
        {
            "title": pair("Реализуем и проверяем", "Build and verify"),
            "text": pair(
                "Разрабатываю, показываю промежуточный результат, проверяю основной сценарий и ошибки.",
                "I implement the system, share progress and test both the main workflow and failure cases.",
            ),
        },
        {
            "title": pair("Запускаем и передаём", "Launch and hand over"),
            "text": pair(
                "Развёртывание, настройки, документация и передача кода. Дальнейшую поддержку обсуждаем отдельно.",
                "Deployment, configuration, documentation and source handover. Ongoing support is agreed separately.",
            ),
        },
    ],
    "contact_eyebrow": pair("Начнём с вашей задачи", "Start with your problem"),
    "contact_title": pair(
        "Расскажите, что должно работать.", "Tell me what needs to work."
    ),
    "contact_lead": pair(
        "Пришлите описание задачи, ссылку на проект или текущий код. Посмотрю и предложу следующий шаг.",
        "Send a brief, a project link or your existing code. I'll take a look and suggest the next step.",
    ),
    "contact_hint": pair(
        "Для новой разработки, доработки проекта или предложения о работе.",
        "For new builds, existing projects and engineering roles.",
    ),
    "footer": pair(
        "Python Backend / AI Integration Developer. От задачи — до работающей системы.",
        "Python Backend / AI Integration Developer. From the problem to a working system.",
    ),
    "menu": pair("Открыть меню", "Open navigation"),
    "skip": pair("К содержимому", "Skip to content"),
    "all": pair("Все", "All"),
    "empty": pair(
        "В этом направлении пока нет кейсов.", "No projects in this category yet."
    ),
    "service_problems": pair("Знакомая ситуация?", "Sound familiar?"),
    "service_deliver": pair("Что могу сделать", "What I can build"),
    "relevant": pair("Релевантные проекты", "Relevant projects"),
    "faq": pair("Перед началом работы", "Before we start"),
    "related": pair("Смежные задачи", "Related services"),
    "engineering": pair("Инженерные решения", "Engineering decisions"),
    "gallery": pair("Как устроен продукт", "Inside the product"),
    "gallery_hint": pair(
        "Нажмите на изображение, чтобы рассмотреть детали.",
        "Open an image to inspect the details.",
    ),
    "next": pair("Следующий проект", "Next project"),
    "back": pair("Все проекты", "All projects"),
    "close": pair("Закрыть изображение", "Close image"),
    "prev_image": pair("Предыдущее изображение", "Previous image"),
    "next_image": pair("Следующее изображение", "Next image"),
    "diagram": pair(
        "Схема по материалам проекта", "Diagram based on project materials"
    ),
    "work_title": pair("Другие задачи. Та же инженерия.", "More work. The same care."),
    "work_lead": pair(
        "Небольшие продукты, интеграции и эксперименты. Назначение, подход и подтверждённый технологический контур.",
        "Smaller products, integrations and experiments. Their purpose, approach and documented technology.",
    ),
    "services_title": pair("Разработка под задачу.", "Engineering for your problem."),
    "services_lead": pair(
        "Python backend, Telegram, сбор данных и AI. Новая система или доработка существующей — начнём с того, что нужно вашему проекту.",
        "Python backends, Telegram, data collection and AI. Whether you need a new system or help with an existing one, the problem comes first.",
    ),
    "not_found": pair("Этой страницы нет.", "This page doesn't exist."),
    "go_home": pair("На главную", "Back home"),
    "overview": pair("Обзор", "Overview"),
}

CATEGORIES = [
    {"id": "backend", "label": pair("Backend", "Backend")},
    {"id": "ai", "label": pair("AI / RAG", "AI / RAG")},
    {"id": "telegram", "label": pair("Telegram", "Telegram")},
    {"id": "parsing", "label": pair("Парсинг / автоматизация", "Parsing / automation")},
    {"id": "integrations", "label": pair("Интеграции", "Integrations")},
]

SERVICES = [
    {
        "slug": "python-backend",
        "code": "01 / BACKEND",
        "icon": "{ }",
        "title": pair("Python backend", "Python backends"),
        "headline": pair(
            "Backend, на который можно опереться.", "A backend you can rely on."
        ),
        "summary": pair(
            "Django, FastAPI, API и интеграции. Новая разработка и восстановление существующих проектов.",
            "Django, FastAPI, APIs and integrations. New systems and repairs to existing projects.",
        ),
        "lead": pair(
            "Разрабатываю серверную логику, API и фоновые процессы. Если Python-проект уже есть, но не работает — начну с диагностики, а не с переписывания всего кода.",
            "I build server-side workflows, APIs and background jobs. If your Python project already exists but doesn't work, I'll begin with diagnosis and keep what can be kept.",
        ),
        "problems": pair(
            [
                "Предыдущий разработчик ушёл, проект остался незавершённым",
                "API падает, фоновые задачи теряются или сайт отдаёт 502",
                "Данные и бизнес-правила разнесены по таблицам и скриптам",
            ],
            [
                "The previous developer left an unfinished project",
                "An API fails, background jobs disappear, or the site returns 502",
                "Data and business rules are scattered across spreadsheets and scripts",
            ],
        ),
        "deliverables": [
            {
                "title": pair("API и доменная логика", "APIs & business logic"),
                "text": pair(
                    "REST API, модели данных, роли и права, интеграции с внешними сервисами и CRM.",
                    "REST APIs, data models, roles, permissions and integrations with external services and CRMs.",
                ),
            },
            {
                "title": pair(
                    "Фоновые процессы и данные", "Background processing & data"
                ),
                "text": pair(
                    "PostgreSQL, очереди Redis/Celery, повторные попытки, контроль состояний и обработка ошибок.",
                    "PostgreSQL, Redis/Celery queues, retries, explicit states and error handling.",
                ),
            },
            {
                "title": pair("Доработка и запуск", "Repair & deployment"),
                "text": pair(
                    "Диагностика чужого кода, исправление ошибок, Docker, VPS, Nginx/Gunicorn и CI/CD.",
                    "Reviewing unfamiliar code, fixing bugs, Docker, VPS deployment, Nginx/Gunicorn and CI/CD.",
                ),
            },
        ],
        "tags": [
            "Python",
            "Django",
            "FastAPI",
            "PostgreSQL",
            "Redis",
            "Celery",
            "Docker",
            "Nginx",
            "CI/CD",
        ],
        "projects": [
            "meatbot-production-crm",
            "hr-corporate-platform",
            "underground-taxi-analytics",
        ],
        "flow": [
            "Web / Telegram",
            "Django / FastAPI",
            "PostgreSQL + workers",
            "API / CRM",
        ],
        "faq": [
            {
                "q": pair(
                    "Можно прийти с чужим незавершённым кодом?",
                    "Can you take over another developer's code?",
                ),
                "a": pair(
                    "Да. Сначала воспроизведу проблему, изучу архитектуру и предложу, что сохранить, исправить или заменить. При неизвестном объёме начнём с платной диагностики.",
                    "Yes. I'll reproduce the issue, review the architecture and propose what to keep, fix or replace. For unclear scope, we can start with a paid diagnostic review.",
                ),
            },
            {
                "q": pair(
                    "Вы занимаетесь развёртыванием?", "Do you handle deployment?"
                ),
                "a": pair(
                    "Да: Docker, VPS, reverse proxy и CI/CD входят в мой опыт. Доступы и границы работ согласуем до начала.",
                    "Yes. My work includes Docker, VPS hosting, reverse proxies and CI/CD. We agree access and scope before starting.",
                ),
            },
            {
                "q": pair(
                    "Как оценить сроки и стоимость?",
                    "How do you estimate cost and delivery?",
                ),
                "a": pair(
                    "После описания сценария и просмотра текущего проекта. Если есть неизвестные, выделим диагностику или первый ограниченный этап.",
                    "After reviewing the workflow and the existing project. If there are unknowns, we can isolate a diagnostic stage or a small first milestone.",
                ),
            },
        ],
        "seo": pair(
            "Python разработчик — Django, FastAPI и доработка backend | Rexileer",
            "Python backend developer — Django, FastAPI & project rescue | Rexileer",
        ),
    },
    {
        "slug": "telegram-bots",
        "code": "02 / TELEGRAM",
        "icon": "↗",
        "title": pair("Telegram-боты", "Telegram bots"),
        "headline": pair(
            "Бот как часть вашего бизнеса.", "A bot that fits your business."
        ),
        "summary": pair(
            "Платежи, подписки, каталоги и рабочие процессы. Бот, backend и админка в одном контуре.",
            "Payments, subscriptions, catalogs and team workflows. Connected to a backend and an admin interface.",
        ),
        "lead": pair(
            "Создаю Telegram-сервисы на Aiogram: от клиентского сценария до платежей, базы данных и админки. Дорабатываю существующих ботов и связываю их с CRM/API.",
            "I build Telegram services with Aiogram, from the user flow to payments, storage and administration. I also extend existing bots and connect them to CRMs and APIs.",
        ),
        "problems": pair(
            [
                "Оплаты и доступы приходится проверять вручную",
                "Бот вырос, но данные, админка и фоновые задачи не связаны",
                "Существующий бот ломается в многошаговых сценариях",
            ],
            [
                "Payments and access are checked manually",
                "The bot has grown, but its data, admin and jobs aren't connected",
                "An existing bot breaks during multi-step workflows",
            ],
        ),
        "deliverables": [
            {
                "title": pair("Клиентские сценарии", "User workflows"),
                "text": pair(
                    "Каталоги, заказы, подписки, формы и уведомления. Явные состояния и восстановление прерванных диалогов.",
                    "Catalogs, orders, subscriptions, forms and notifications. Explicit states and recovery of interrupted conversations.",
                ),
            },
            {
                "title": pair("Платежи и интеграции", "Payments & integrations"),
                "text": pair(
                    "YooKassa, выдача доступа, CRM и внешние API. Подтверждение оплаты и повторные события учитываются в логике.",
                    "YooKassa, access provisioning, CRMs and external APIs. Payment confirmation and repeated events are handled in the workflow.",
                ),
            },
            {
                "title": pair("Управление и доработка", "Operations & improvements"),
                "text": pair(
                    "Django Admin, справочники, фоновые задачи и рассылки. Могу подключиться к текущему коду.",
                    "Django Admin, reference data, background jobs and messaging. I can work with your existing codebase.",
                ),
            },
        ],
        "tags": [
            "Python",
            "Aiogram",
            "Telegram Bot API",
            "Django",
            "FastAPI",
            "PostgreSQL",
            "Redis",
            "Celery",
            "YooKassa",
        ],
        "projects": [
            "payment-broadcast-bot",
            "steps-corporate-gamification",
            "hr-corporate-platform",
        ],
        "flow": [
            "Telegram",
            "Aiogram / states",
            "Backend + database",
            "Payments / CRM",
        ],
        "faq": [
            {
                "q": pair(
                    "Можно доработать уже запущенного бота?",
                    "Can you improve a bot that's already live?",
                ),
                "a": pair(
                    "Да. Изучу обработчики, модели данных и текущий запуск. Согласуем, как выпускать изменения и проверять сценарии.",
                    "Yes. I'll review the handlers, data model and deployment, then agree how to release and verify changes.",
                ),
            },
            {
                "q": pair(
                    "Нужна ли отдельная админка?", "Does a bot need an admin interface?"
                ),
                "a": pair(
                    "Зависит от задачи. Если нужно управлять каталогом, контентом, оплатами или пользователями — админка позволяет делать это без правок кода.",
                    "It depends. If you need to manage a catalog, content, payments or users, an admin interface lets you do that without editing code.",
                ),
            },
            {
                "q": pair("Можно связать бота с CRM?", "Can the bot connect to a CRM?"),
                "a": pair(
                    "Да, через доступный API или webhook. Сначала проверим возможности CRM, права доступа и события, которые нужно передавать.",
                    "Yes, using the available API or webhooks. First we'll check the CRM capabilities, access and events that need to be exchanged.",
                ),
            },
        ],
        "seo": pair(
            "Разработка Telegram-ботов — Aiogram, платежи и CRM | Rexileer",
            "Telegram bot development — Aiogram, payments & CRM | Rexileer",
        ),
    },
    {
        "slug": "parsers-automation",
        "code": "03 / DATA",
        "icon": "⇄",
        "title": pair("Парсинг и автоматизация", "Parsing & automation"),
        "headline": pair(
            "Данные приходят. Процессы работают.",
            "Collect the data. Connect the workflow.",
        ),
        "summary": pair(
            "Сбор из сайтов, Telegram и API. Очереди, фильтрация, нормализация и управляемый результат.",
            "Collection from websites, Telegram and APIs. Queues, filtering, normalization and a usable result.",
        ),
        "lead": pair(
            "Разрабатываю системы регулярного сбора данных: несколько источников, фоновые исполнители, хранение, проверка качества и доставка результата. Не только скрипт для одного запуска.",
            "I build repeatable data collection systems: multiple sources, background workers, storage, quality checks and delivery. The pipeline can keep running after the first import.",
        ),
        "problems": pair(
            [
                "Нужные данные приходится собирать с нескольких площадок вручную",
                "Парсер останавливается, появляются дубли и разные форматы",
                "Excel-прайсы и выгрузки требуют постоянной ручной подготовки",
            ],
            [
                "Useful data has to be gathered manually from several sources",
                "A parser stops, creates duplicates or produces inconsistent formats",
                "Excel price lists and exports need recurring manual preparation",
            ],
        ),
        "deliverables": [
            {
                "title": pair("Регулярный сбор", "Repeatable collection"),
                "text": pair(
                    "Сайты, Telegram и API; Selenium/Playwright, прокси, расписания, ограничения и повторные попытки.",
                    "Websites, Telegram and APIs; Selenium/Playwright, proxies, schedules, limits and retries.",
                ),
            },
            {
                "title": pair("Данные в единой форме", "Consistent data"),
                "text": pair(
                    "Нормализация, дедупликация, фильтры и PostgreSQL. Для таблиц — preview и сопоставление колонок.",
                    "Normalization, deduplication, filters and PostgreSQL. For spreadsheets: previews and column mapping.",
                ),
            },
            {
                "title": pair(
                    "Результат в вашем процессе", "Results where you need them"
                ),
                "text": pair(
                    "Очереди и статусы задач, мониторинг, уведомления, выгрузка в Excel, Google Sheets или API.",
                    "Queues, task states, monitoring, notifications and delivery to Excel, Google Sheets or an API.",
                ),
            },
        ],
        "tags": [
            "Python",
            "FastAPI",
            "Django",
            "Selenium",
            "Playwright",
            "Pyrogram",
            "Celery",
            "Redis",
            "PostgreSQL",
            "openpyxl",
        ],
        "projects": ["avito-parts-parser", "priceflow-ai", "miyoumi-vk-analytics"],
        "flow": [
            "Sites / Telegram / API",
            "Workers + retries",
            "Normalize + store",
            "Excel / API / alerts",
        ],
        "faq": [
            {
                "q": pair(
                    "Чем это отличается от одноразового скрипта?",
                    "How is this different from a one-off script?",
                ),
                "a": pair(
                    "Есть расписание, статусы, очереди, повторы, хранение и контроль ошибок. Можно понять, что собралось, а что требует внимания.",
                    "A system has schedules, states, queues, retries, storage and error visibility. You can tell what was collected and what needs attention.",
                ),
            },
            {
                "q": pair(
                    "Какие источники можно подключить?",
                    "Which sources can be connected?",
                ),
                "a": pair(
                    "Сайты, Telegram и внешние API. Возможность и способ сбора определяются после просмотра источника и доступных интерфейсов.",
                    "Websites, Telegram and external APIs. Feasibility and collection methods depend on the source and its available interfaces.",
                ),
            },
            {
                "q": pair(
                    "Что делать, если сайт изменился и парсер сломался?",
                    "What if the source changes and breaks the parser?",
                ),
                "a": pair(
                    "Воспроизведу сбой, проверю получение страницы и извлечение полей. Доработаем сбор и добавим контроль нужных ошибок.",
                    "I'll reproduce the failure and check both page access and field extraction, then update collection and relevant failure checks.",
                ),
            },
        ],
        "seo": pair(
            "Парсеры Python и автоматизация — сбор данных и API | Rexileer",
            "Python parsing & automation — data collection and APIs | Rexileer",
        ),
    },
    {
        "slug": "ai-rag",
        "code": "04 / AI",
        "icon": "✳",
        "title": pair("AI / RAG-интеграции", "AI / RAG integrations"),
        "headline": pair(
            "AI, который работает с вашими данными.", "AI connected to your data."
        ),
        "summary": pair(
            "База знаний, поиск по документам, AI-оценка и CRM. Модель внутри понятного рабочего сценария.",
            "Knowledge bases, document retrieval, AI scoring and CRMs. A model inside a defined workflow.",
        ),
        "lead": pair(
            "Интегрирую LLM в конкретные процессы: консультант по каталогу и документам, оценка заявок, ответы в CRM. Проектирую загрузку знаний, retrieval, управление промптами и передачу человеку.",
            "I integrate LLMs into specific workflows: answering from a catalog and documents, scoring inquiries and replying in a CRM. The work includes ingestion, retrieval, prompt management and human handoff.",
        ),
        "problems": pair(
            [
                "Документы есть, но сотрудникам сложно быстро найти нужный ответ",
                "Чат с моделью не опирается на каталог и выдаёт неподтверждённые факты",
                "Лиды и обращения нужно оценивать по правилам вашего проекта",
            ],
            [
                "Documents exist, but the right answer is hard to find",
                "The model ignores the catalog and makes unsupported claims",
                "Inquiries need to be assessed against your project's criteria",
            ],
        ),
        "deliverables": [
            {
                "title": pair(
                    "Управляемая база знаний", "A maintainable knowledge base"
                ),
                "text": pair(
                    "Обработка DOCX/XLSX, embeddings, vector и hybrid search. Источники и каталог можно обновлять.",
                    "DOCX/XLSX ingestion, embeddings, vector and hybrid search. Source documents and catalog data remain maintainable.",
                ),
            },
            {
                "title": pair("Рабочая интеграция", "A workflow integration"),
                "text": pair(
                    "Bitrix24, Telegram или API; фоновые задачи, история диалогов и AI scoring/classification.",
                    "Bitrix24, Telegram or an API; background jobs, conversation history and AI scoring/classification.",
                ),
            },
            {
                "title": pair("Контроль ответа", "Answer controls"),
                "text": pair(
                    "Контекст из найденных источников, ограничения на факты, контроль ошибок и сценарий передачи человеку. Абсолютную безошибочность модели не обещаю.",
                    "Retrieved source context, factual constraints, failure handling and a human handoff. I don't promise that a model will never make a mistake.",
                ),
            },
        ],
        "tags": [
            "Python",
            "Django",
            "DRF",
            "pgvector",
            "FastEmbed",
            "PostgreSQL",
            "Redis / RQ",
            "OpenAI-compatible API",
            "Bitrix24",
        ],
        "projects": [
            "ai-consultant-bitrix-rag",
            "ai-lead-scoring",
            "ai-media-platform",
        ],
        "flow": [
            "Documents / catalog",
            "Embeddings + retrieval",
            "LLM + controls",
            "CRM / Telegram / human",
        ],
        "faq": [
            {
                "q": pair(
                    "Чем RAG отличается от обычного чата с LLM?",
                    "How is RAG different from a basic LLM chat?",
                ),
                "a": pair(
                    "Перед ответом система ищет релевантные фрагменты ваших документов и передаёт их модели. Качество зависит от источников, retrieval и правил ответа.",
                    "Before answering, the system retrieves relevant passages from your documents and supplies them to the model. Quality depends on sources, retrieval and answer rules.",
                ),
            },
            {
                "q": pair(
                    "Можно использовать GigaChat или другую модель?",
                    "Can we use GigaChat or another model?",
                ),
                "a": pair(
                    "Провайдера выбираем по API, данным, ограничениям и бюджету. В моих кейсах есть OpenAI-compatible API; другого провайдера сначала проверим на небольшом сценарии.",
                    "We'll choose a provider based on its API, data requirements, constraints and budget. My projects include OpenAI-compatible APIs; a different provider would first be validated on a small workflow.",
                ),
            },
            {
                "q": pair(
                    "Можно подключить внутренние документы и CRM?",
                    "Can this connect internal documents and a CRM?",
                ),
                "a": pair(
                    "Да. В кейсе AI Consultant реализованы DOCX/XLSX ingestion, hybrid retrieval и Bitrix24 webhooks. Для вашего проекта определим права, обновление знаний и критерии качества.",
                    "Yes. AI Consultant includes DOCX/XLSX ingestion, hybrid retrieval and Bitrix24 webhooks. For your project we'll define permissions, updates and quality criteria.",
                ),
            },
        ],
        "seo": pair(
            "AI-интеграции и RAG-разработка — документы, LLM, CRM | Rexileer",
            "AI integrations & RAG development — documents, LLMs & CRM | Rexileer",
        ),
    },
]

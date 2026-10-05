# Аудит визуалов — 5 октября 2026

Проверены все 168 PNG: 108 уникальных файлов, 60 точных дублей в fl-ready. Исходники RGB, без прозрачности. Исходные размеры: от 1265×712 до 1600×1200. Исходная папка сохранена без изменений.

## Использовано

| Папка → кейс | Обложка | Дополнительные материалы |
|---|---|---|
| ai-leads → ai-lead-scoring | raw/analytics.png | raw/leads-list.png, raw/lead-ai-score.png, raw/project-settings.png, 05-architecture.png |
| ai-consultant → ai-consultant-bitrix-rag | raw/products.png | raw/swagger.png, raw/messages.png, raw/prompts.png, 05-architecture.png |
| avito-parser → avito-parts-parser | raw/flower.png | raw/swagger.png, raw/health-response.png, 05-architecture.png |
| meatbot → meatbot-production-crm | raw/workstation-weighing.png | raw/raw-batches.png, raw/workstation-result.png, 05-architecture.png |
| taxi-analytics → underground-taxi-analytics | raw/dashboard-overview.png | raw/drivers.png, raw/cities.png, raw/anomalies.png, 05-architecture.png |
| priceflow-ai → priceflow-ai | raw/upload-preview.png | raw/parsed-items.png, raw/catalog.png, raw/project.png, 05-architecture.png |
| miyoumi-analytics → miyoumi-vk-analytics | raw/publications.png | raw/anomalies.png, raw/sheets.png, 05-architecture.png |
| payment-bot → payment-broadcast-bot | 02-workflow.png | 03-result.png, 04-technical.png, 05-architecture.png |
| steps-bot → steps-corporate-gamification | 02-workflow.png | 03-result.png, 04-technical.png, 05-architecture.png |
| mexc-scalping → mexc-scalping-autobuy | 02-workflow.png | 03-result.png, 04-technical.png, 05-architecture.png |

Полный список исходник → версия сайта → размещение: `assets-manifest.json`.

Все оригинальные кадры конвертированы в lossless WebP в исходном разрешении. Для карточек подготовлены варианты 640/960 px без увеличения исходника; интерфейсы не перерисовывались, не растягивались и не кадрировались. В галерее можно открыть исходное разрешение. Размеры зарезервированы в HTML.

Payment / Steps / MEXC: предоставленные диалоги восстановлены по handlers, не являются снятыми скриншотами. Это явно подписано на сайте. MEXC не заявляет доходность; данные условные. Miyoumi: raw/dashboard с чрезмерными демонстрационными показателями не используется; выбран экран публикаций, значения не выдаются за коммерческий результат.

## Пропущено

- `fl-ready/**`: 60 побайтовых дублей для другой площадки.
- `*/contact-sheet.png`: служебные контактные листы.
- `*/cover.png`: маркетинговые композиции с жёстким mobile-crop интерфейса; выбран полный реальный интерфейс либо подписанная иллюстрация сценария.
- Слайды 01–04 с повторением выбранных raw-кадров: лишняя рамка и русский текст внутри изображения; исходные интерфейсы чище и читаются лучше.

- ai-leads: raw/admin-home.png, raw/lead-detail.png — общая админка и повторение выбранной карточки оценки.
- ai-consultant: raw/admin-home.png, raw/dialogs.png — общая админка и список диалогов; продукты, сообщения и настройки лучше показывают работу системы.
- meatbot: raw/admin-home.png, raw/finished-goods.png — общая админка и вторичный список; выбраны связанные шаги производственного сценария.
- taxi-analytics: raw/admin.png, raw/draws.png — вторичные экраны; оставлены обзор, водители, города и аномалии.
- priceflow-ai: raw/dashboard.png, raw/supplier.png — вторичные экраны; выбран путь от загрузки прайса до каталога и проекта.
- miyoumi-analytics: raw/bloggers.png, raw/collector.png — вторичные списки; raw/dashboard.png исключён из-за чрезмерных демонстрационных показателей.

## Чего ещё не хватает

Для трёх Telegram-кейсов желательны обезличенные скриншоты реальных чатов вместо иллюстраций. Для AI Consultant полезен реальный диалог Bitrix24 со ссылкой на источник. Для Avito — анонимная выдача собранных данных.

Для остальных кейсов ниже используются типографические технические placeholders с подтверждённым стеком; для AI Media сохранён существующий SVG. Нужны реальные кадры интерфейса, без приватных данных. Рекомендуемая обложка: 16:9, минимум 1280×720 (лучше 1920×1080); дополнительные кадры можно оставить в исходном aspect ratio.

- bozon-medpreds: создание/завершение визита в боте и история визитов в CRM.
- ai-media-platform: реальный сценарий генерации и готовый результат; отдельно Mini App, если доступен.
- go-scalper: графики мониторинга и схема Go → gRPC → Rust. Не нужны обещания доходности.
- hr-corporate-platform: выдача документа, подтверждение сотрудника и административная аналитика.
- bozon-medpreds-learn: материал обучения, прохождение теста, просмотр результатов.
- bozon-samples: создание заявки и административная обработка её статуса.
- auto-listings-parser: фильтры и карточка найденного автомобиля в Telegram/web.
- freelance-bot: лента заявок и настройка подписки на категории.
- repair-requests-bot: проект с фильтрами и обезличенная найденная заявка.
- church-bot: форма имён, подтверждение заказа и административная карточка.
- contact-parser-multi-tenant: карточка лида и настройки отдельного пользовательского проекта.
- mini-crm-lead-distribution: Swagger и пример распределения обезличенного лида.
- any-parse-bot: команда бота и реальный результат извлечения структурированных данных.
- real-estate-parser: сначала найти и проверить исходники; затем подтвердить существующие фильтры и результат сбора.
- wallet-risk-scorer: реальный API-ответ с объяснением оценки и таблица признаков.
- shopi: каталог, корзина и оформление заказа; Swagger как дополнительный технический кадр.

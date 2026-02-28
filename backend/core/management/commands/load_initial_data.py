"""Загружает начальные тексты/навыки/проекты из текущего фронта (одноразово)."""
from django.core.management.base import BaseCommand
from core.models import SiteText, Skill, Project

# Минимальный набор ключей из data-i18n и copy в script.js
DEFAULT_TEXTS = [
    ("brand.name", "en", "Rexileer"), ("brand.name", "ru", "Rexileer"),
    ("nav.about", "en", "About"), ("nav.about", "ru", "Обо мне"),
    ("nav.skills", "en", "Skills"), ("nav.skills", "ru", "Навыки"),
    ("nav.projects", "en", "Projects"), ("nav.projects", "ru", "Проекты"),
    ("nav.contact", "en", "Contact"), ("nav.contact", "ru", "Контакты"),
    ("langToggle.label", "en", "Language"), ("langToggle.label", "ru", "Язык"),
    ("hero.eyebrow", "en", "Backend Developer"), ("hero.eyebrow", "ru", "Бэкенд-разработчик"),
    ("hero.title", "en", "Building reliable backend systems with Python."),
    ("hero.title", "ru", "Создаю надёжные бэкенд-системы на Python."),
    ("hero.subtitle", "en", "I design and evolve data-stream services with attention to stability, observability, and fast feature delivery."),
    ("hero.subtitle", "ru", "Проектирую и поддерживаю сервисы данных с фокусом на стабильность, наблюдаемость и быструю доставку фич."),
    ("hero.ctaProjects", "en", "See projects"), ("hero.ctaProjects", "ru", "Смотреть проекты"),
    ("hero.ctaContact", "en", "Let's connect"), ("hero.ctaContact", "ru", "Связаться"),
    ("about.eyebrow", "en", "Profile"), ("about.eyebrow", "ru", "Профиль"),
    ("about.title", "en", "Short intro"), ("about.title", "ru", "Коротко обо мне"),
    ("about.paragraph1", "en", "I help teams and companies take solutions from prototype to production, engineering architecture and CI/CD that handle real-world load."),
    ("about.paragraph1", "ru", "Помогаю командам и компаниям выводить решения из прототипа в продакшн, проектируя архитектуру и CI/CD под реальные нагрузки."),
    ("about.paragraph2", "en", "I combine engineering discipline with pragmatism — shipping production systems without losing control of quality or infrastructure."),
    ("about.paragraph2", "ru", "Сочетаю инженерный подход с прагматикой — выпускаю продакшн-решения без потери контроля над качеством и инфраструктурой."),
    ("skills.eyebrow", "en", "Stack"), ("skills.eyebrow", "ru", "Стек"),
    ("skills.title", "en", "Skills & tools"), ("skills.title", "ru", "Навыки и инструменты"),
    ("skills.description", "en", "I work across the Python ecosystem, orchestrating services with cloud-native tooling and modern DevOps practices."),
    ("skills.description", "ru", "Работаю в экосистеме Python, создаю микросервисы и backend с Docker, Redis, Celery и CI/CD."),
    ("projects.eyebrow", "en", "Selected Work"), ("projects.eyebrow", "ru", "Избранное"),
    ("projects.title", "en", "Projects"), ("projects.title", "ru", "Проекты"),
    ("contact.eyebrow", "en", "Let's Talk"), ("contact.eyebrow", "ru", "На связи"),
    ("contact.title", "en", "Contact"), ("contact.title", "ru", "Контакты"),
    ("contact.description", "en", "Reach out if you're looking for a backend engineer to ship reliable services or to collaborate on new ideas."),
    ("contact.description", "ru", "Доступен для удалённой работы (full-time / contract). Пишите, если нужен backend-инженер — обсудим объём и сроки."),
    ("contact.labels.email", "en", "Email"), ("contact.labels.email", "ru", "Email"),
    ("contact.labels.github", "en", "GitHub"), ("contact.labels.github", "ru", "GitHub"),
    ("contact.labels.linkedin", "en", "LinkedIn"), ("contact.labels.linkedin", "ru", "LinkedIn"),
    ("contact.labels.telegram", "en", "Telegram"), ("contact.labels.telegram", "ru", "Telegram"),
    ("footer.note", "en", " 2025 Rexileer. Available for remote opportunities."),
    ("footer.note", "ru", " 2025 Rexileer. Открыт к удалённым предложениям."),
]

DEFAULT_SKILLS_EN = [
    "Python", "Django", "FastAPI", "PostgreSQL", "SQLAlchemy",
    "Docker · Docker Compose", "GitLab CI · GitHub Actions",
    "Celery", "Linux", "Nginx", "Redis", "Kubernetes (basic)",
]
DEFAULT_SKILLS_RU = DEFAULT_SKILLS_EN

DEFAULT_PROJECTS = [
    {"slug": "scalping-bot", "meta_en": "Live Demo", "meta_ru": "Демо",
     "title_en": "Crypto Scalping MEXC", "title_ru": "Крипто скальпинг MEXC",
     "description_en": "Crypto trading bot executing scalping strategies via the MEXC API.",
     "description_ru": "Бот для криптотрейдинга, исполняющий стратегии скальпинга через MEXC API.",
     "tags": ["Aiogram", "Django", "PostgreSQL", "Docker Compose", "GitHub Actions"],
     "links": [{"type": "demo", "href": "https://t.me/scalpingtest_bot", "label": {"en": "Open demo", "ru": "Открыть демо"}},
               {"type": "github", "href": "https://github.com/rexileer/skalping-bot-demo", "label": {"en": "GitHub", "ru": "GitHub"}}], "order": 0},
    {"slug": "steps-bot", "meta_en": "Featured", "meta_ru": "Витрина",
     "title_en": "Steps Bot", "title_ru": "Шаги-бот",
     "description_en": "Bot for tracking steps/walks, balance and orders. Admin API and optional Django admin.",
     "description_ru": "Бот для учета шагов/прогулок, баланса и заказов. Есть admin API и опциональная Django-админка.",
     "tags": ["Aiogram", "Django", "PostgreSQL", "Docker Compose", "GitHub Actions", "FastAPI"],
     "links": [{"type": "github", "href": "https://github.com/rexileer/steps-bot-demo", "label": {"en": "GitHub", "ru": "GitHub"}}], "order": 1},
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for key, lang, value in DEFAULT_TEXTS:
            SiteText.objects.get_or_create(key=key, lang=lang, defaults={"value": value})
        for i, t in enumerate(DEFAULT_SKILLS_EN):
            Skill.objects.get_or_create(lang="en", text=t, defaults={"order": i})
        for i, t in enumerate(DEFAULT_SKILLS_RU):
            Skill.objects.get_or_create(lang="ru", text=t, defaults={"order": i})
        for p in DEFAULT_PROJECTS:
            slug = p["slug"]
            order = p["order"]
            Project.objects.get_or_create(slug=slug, defaults={
                "meta_en": p["meta_en"], "meta_ru": p["meta_ru"],
                "title_en": p["title_en"], "title_ru": p["title_ru"],
                "description_en": p.get("description_en", ""), "description_ru": p.get("description_ru", ""),
                "tags": p.get("tags", []), "links": p.get("links", []), "order": order,
            })
        self.stdout.write(self.style.SUCCESS("Initial data loaded."))

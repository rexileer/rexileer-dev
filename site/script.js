const copy = {
  en: {
    brand: { name: "Rexileer" },
    nav: {
      about: "About",
      skills: "Skills",
      projects: "Projects",
      contact: "Contact",
    },
    langToggle: { label: "Language" },
    hero: {
      eyebrow: "Backend Developer",
      title: "Building reliable backend systems with Python.",
      subtitle:
        "I design and evolve data-stream services with attention to stability, observability, and fast feature delivery.",
      ctaProjects: "See projects",
      ctaContact: "Let's connect",
    },
    about: {
      eyebrow: "Profile",
      title: "Short intro",
      paragraph1:
        "I help teams and companies take solutions from prototype to production, engineering architecture and CI/CD that handle real-world load.",
      paragraph2:
        "I combine engineering discipline with pragmatism — shipping production systems without losing control of quality or infrastructure.",
    },
    skills: {
      eyebrow: "Stack",
      title: "Skills & tools",
      description:
        "I work across the Python ecosystem, orchestrating services with cloud-native tooling and modern DevOps practices.",
    },
    projects: {
      eyebrow: "Selected Work",
      title: "Projects",
    },
    contact: {
      eyebrow: "Let’s Talk",
      title: "Contact",
      description:
        "Reach out if you’re looking for a backend engineer to ship reliable services or to collaborate on new ideas.",
      labels: {
        email: "Email",
        github: "GitHub",
        linkedin: "LinkedIn",
        telegram: "Telegram",
      },
    },
    footer: {
      note: " 2025 Rexileer. Available for remote opportunities.",
    },
  },
  ru: {
    brand: { name: "Rexileer" },
    nav: {
      about: "Обо мне",
      skills: "Навыки",
      projects: "Проекты",
      contact: "Контакты",
    },
    langToggle: { label: "Язык" },
    hero: {
      eyebrow: "Бэкенд-разработчик",
      title: "Создаю надёжные бэкенд-системы на Python.",
      subtitle:
        "Проектирую, внедряю и поддерживаю сервисы, работающие с данными, концентрируясь на прозрачности, поддерживаемости и измеримом результате.",
      ctaProjects: "Смотреть проекты",
      ctaContact: "Связаться",
    },
    about: {
      eyebrow: "Профиль",
      title: "Коротко обо мне",
      paragraph1:
        "Помогаю командам и компаниям выводить решения из прототипа в продакшн, проектируя архитектуру и CI/CD под реальные нагрузки.",
      paragraph2:
        "Сочетаю инженерный подход с прагматикой — выпускаю продакшн-решения без потери контроля над качеством и инфраструктурой.",
    },
    skills: {
      eyebrow: "Стек",
      title: "Навыки и инструменты",
      description:
        "Работаю в экосистеме Python, создаю микросервисы и backend-архитектуру с использованием Docker, Redis, Celery и CI/CD-практик.",
    },
    projects: {
      eyebrow: "Избранное",
      title: "Проекты",
    },
    contact: {
      eyebrow: "На связи",
      title: "Контакты",
      description:
        "Доступен для удалённой работы (full-time / contract). Пишите, если нужен инженер по backend-части — обсудим объём и сроки.",
      labels: {
        email: "Email",
        github: "GitHub",
        linkedin: "LinkedIn",
        telegram: "Telegram",
      },
    },
    footer: {
      note: " 2025 Rexileer. Открыт к удалённым предложениям.",
    },
  },
};

const skills = {
  en: [
    "Python",
    "Django",
    "FastAPI",
    "PostgreSQL",
    "SQLAlchemy",
    "Docker · Docker Compose",
    "GitLab CI · GitHub Actions",
    "Selenium Wire · undetected-chromedriver",
    "Celery",
    "Linux",
    "Monitoring: Prometheus & Grafana (worked with)",
    "Nginx",
    "Go · Rust — cross-stack tooling (personal projects)",
    "Redis",
    "WebSockets · Background workers · Observability",
    "Kubernetes (basic)",
  ],
  ru: [
    "Python",
    "Django",
    "FastAPI",
    "PostgreSQL",
    "SQLAlchemy",
    "Docker · Docker Compose",
    "GitLab CI · GitHub Actions",
    "Selenium Wire · undetected-chromedriver",
    "Celery",
    "Linux",
    "Monitoring: Prometheus & Grafana (worked with)",
    "Nginx",
    "Go · Rust — cross-stack tooling (personal projects)",
    "Redis",
    "WebSockets · Background workers · Observability",
    "Kubernetes (basic)",
  ],
};

const projects = [
  {
    id: "scalping-bot",
    meta: { en: "Live Demo", ru: "Демо" },
    title: {
      en: "Crypto Scalping MEXC",
      ru: "Крипто скальпинг MEXC",
    },
    description: {
      en: "Crypto trading bot executing scalping strategies via the MEXC API. Handles live market streams, trade automation, and monitoring.",
      ru: "Бот для криптотрейдинга, исполняющий стратегии скальпинга через MEXC API. Работает с рыночными потоками в реальном времени, автоматизирует сделки и мониторинг.",
    },
    tags: [
      "Aiogram",
      "Django",
      "PostgreSQL",
      "Docker Compose",
      "GitHub Actions",
    ],
    links: [
      {
        type: "demo",
        href: "https://t.me/scalpingtest_bot",
        label: { en: "Open demo", ru: "Открыть демо" },
      },
      {
        type: "github",
        href: "https://github.com/rexileer/skalping-bot-demo",
        label: { en: "GitHub", ru: "GitHub" },
      },
    ],
  },
  {
    id: "steps-bot",
    meta: { en: "Featured", ru: "Витрина" },
    title: {
      en: "Steps Bot",
      ru: "Шаги-бот",
    },
    description: {
      en: "Bot for tracking steps/walks, balance and orders. There is an admin API and an optional Django admin panel.",
      ru: "Бот для учета шагов/прогулок, баланса и заказов. Есть admin API и опциональная Django-админка.",
    },
    tags: [
      "Aiogram",
      "Django",
      "PostgreSQL",
      "Docker Compose",
      "GitHub Actions",
      "SQLAlchemy + Alembic",
      "FastAPI",
    ],
    links: [
      {
        type: "github",
        href: "https://github.com/rexileer/steps-bot-demo",
        label: { en: "GitHub", ru: "GitHub" },
      },
    ],
  },
  {
    id: "meat-bot",
    meta: { en: "Featured", ru: "Витрина" },
    title: {
      en: "Production System for Meat Factory",
      ru: "Производственная система для мясного завода",
    },
    description: {
      en: "Production system: Telegram bot (workshop) + Django CRM (office).",
      ru: "Производственная система: Telegram‑бот (цех) + Django CRM (офис).",
    },
    tags: [
      "Aiogram",
      "Django",
      "PostgreSQL",
      "Docker Compose",
      "Minio",
      "openpyxl",
      "Redis",
    ],
    links: [
      {
        type: "github",
        href: "https://github.com/rexileer/meat-bot-example",
        label: { en: "GitHub", ru: "GitHub" },
      },
    ],
  },
  {
    id: "freelance-bot",
    meta: { en: "Featured", ru: "Витрина" },
    title: {
      en: "Freelance Bot",
      ru: "Фриланс-бот",
    },
    description: {
      en: "Telegram bot for automating the search and placement of freelance applications.",
      ru: "Телеграм-бот для автоматизации поиска и размещения фриланс-заявок.",
    },
    tags: ["Aiogram", "Django", "PostgreSQL", "Docker Compose", "Telethon"],
    links: [
      {
        type: "github",
        href: "https://github.com/rexileer/freelance-bot-demo",
        label: { en: "GitHub", ru: "GitHub" },
      },
    ],
  },
  {
    id: "payment-broadcast-bot",
    meta: { en: "Featured", ru: "Витрина" },
    title: {
      en: "Payment Broadcast Bot",
      ru: "Бот для рассылки оплаты",
    },
    description: {
      en: "Bot for paid subscriptions/payments and mailings.",
      ru: "Бот для платных подписок/платежей и рассылок.",
    },
    tags: ["Aiogram", "Django", "PostgreSQL", "Docker Compose", "Yookassa API"],
    links: [
      {
        type: "github",
        href: "https://github.com/rexileer/payment-broadcast-bot-example",
        label: { en: "GitHub", ru: "GitHub" },
      },
    ],
  },
  {
    id: "telegram-channel",
    meta: { en: "Telegram Channel", ru: "Телеграм-канал" },
    title: {
      en: "Telegram Channel",
      ru: "Телеграм-канал",
    },
    description: {
      en: "Telegram channel about my experience in various projects.",
      ru: "Телеграм-канал, в котором подробно описывается мой опыт в различных проектах.",
    },
    tags: ["Telegram"],
    links: [
      {
        type: "telegram",
        href: "https://t.me/rexileerdev",
        label: { en: "Open channel", ru: "Открыть канал" },
      },
    ],
  },
];

const storageKey = "rexileer.lang";
const nextLanguageLabel = {
  en: "Switch language to Russian",
  ru: "Переключить язык на английский",
};
const langToggle = document.getElementById("lang-toggle");
const langDisplay = document.querySelector("[data-lang-display]");
const skillsList = document.getElementById("skills-list");
const projectGrid = document.getElementById("project-grid");
const i18nElements = [...document.querySelectorAll("[data-i18n]")];
const contactLabelElements = {
  email: document.querySelector('[data-i18n="contact.labels.email"]'),
  github: document.querySelector('[data-i18n="contact.labels.github"]'),
  linkedin: document.querySelector('[data-i18n="contact.labels.linkedin"]'),
  telegram: document.querySelector('[data-i18n="contact.labels.telegram"]'),
};

function getNestedCopy(lang, key) {
  return key
    .split(".")
    .reduce((acc, part) => (acc ? acc[part] : undefined), copy[lang]);
}

function updateStaticText(lang) {
  i18nElements.forEach((node) => {
    const text = getNestedCopy(lang, node.dataset.i18n);
    if (typeof text === "string") {
      node.textContent = text;
    }
  });
}

function renderSkills(lang) {
  skillsList.innerHTML = "";
  const fragment = document.createDocumentFragment();
  skills[lang].forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    fragment.appendChild(li);
  });
  skillsList.appendChild(fragment);
}

function createLinkElement(link, lang) {
  const anchor = document.createElement("a");
  anchor.className = "project-link";
  anchor.href = link.href;
  anchor.target = "_blank";
  anchor.rel = "noreferrer";
  anchor.textContent = link.label[lang];
  const arrow = document.createElement("span");
  arrow.setAttribute("aria-hidden", "true");
  arrow.textContent = "↗";
  anchor.appendChild(arrow);
  return anchor;
}

function renderProjects(lang) {
  projectGrid.innerHTML = "";
  const fragment = document.createDocumentFragment();

  projects.forEach((project) => {
    const card = document.createElement("article");
    card.className = "project-card";
    card.role = "listitem";

    const meta = document.createElement("span");
    meta.className = "project-meta";
    meta.textContent = project.meta[lang];

    const title = document.createElement("h3");
    title.className = "project-title";
    title.textContent = project.title[lang];

    const description = document.createElement("p");
    description.className = "project-description";
    description.textContent = project.description[lang];

    const tagContainer = document.createElement("div");
    tagContainer.className = "project-tags";
    project.tags.forEach((tag) => {
      const span = document.createElement("span");
      span.className = "project-tag";
      span.textContent = tag;
      tagContainer.appendChild(span);
    });

    const linkContainer = document.createElement("div");
    linkContainer.className = "project-links";
    project.links.forEach((link) => {
      linkContainer.appendChild(createLinkElement(link, lang));
    });

    card.append(meta, title, description, tagContainer, linkContainer);
    fragment.appendChild(card);
  });

  projectGrid.appendChild(fragment);
}

function updateLanguage(lang) {
  document.documentElement.lang = lang;
  if (langDisplay) {
    langDisplay.textContent = lang.toUpperCase();
  }
  updateStaticText(lang);
  renderSkills(lang);
  renderProjects(lang);
  hydrateContactLabels(lang);
  if (langToggle) {
    langToggle.setAttribute("aria-label", nextLanguageLabel[lang]);
    langToggle.dataset.nextLang = lang === "en" ? "ru" : "en";
  }
  localStorage.setItem(storageKey, lang);
}

function initLanguage() {
  const savedLang = localStorage.getItem(storageKey);
  if (savedLang && copy[savedLang]) {
    return savedLang;
  }
  const prefersRu = navigator.language && navigator.language.startsWith("ru");
  return prefersRu ? "ru" : "en";
}

function handleLangToggle() {
  const nextLang = document.documentElement.lang === "en" ? "ru" : "en";
  updateLanguage(nextLang);
}

function hydrateContactLabels(lang) {
  Object.entries(contactLabelElements).forEach(([key, element]) => {
    if (element) {
      const value = copy[lang]?.contact?.labels?.[key];
      if (value) {
        element.textContent = value;
      }
    }
  });
}

function init() {
  const startingLang = initLanguage();
  updateLanguage(startingLang);

  if (langToggle) {
    langToggle.addEventListener("click", () => {
      handleLangToggle();
    });
  }

  window.addEventListener("hashchange", () => {
    const target = document.querySelector(window.location.hash);
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
}

document.addEventListener("DOMContentLoaded", init);

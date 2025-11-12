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
        "I design, ship, and operate data-intensive services with a focus on clarity, maintainability, and measurable impact.",
      ctaProjects: "See projects",
      ctaContact: "Let's connect",
    },
    about: {
      eyebrow: "Profile",
      title: "Short intro",
      paragraph1:
        "I help teams transform prototypes into production services, focusing on resilient architecture, observability, and clean delivery pipelines.",
      paragraph2:
        "My workflow combines disciplined backend engineering with pragmatic deployment strategies so new features reach users quickly and safely.",
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
      note: "© 2025 Rexileer. Available for remote opportunities.",
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
        "Помогаю командам превращать прототипы в продакшн-сервисы, уделяя внимание стабильной архитектуре, наблюдаемости и понятным CI/CD.",
      paragraph2:
        "Сочетаю инженерную дисциплину с прагматичным подходом к деплою, чтобы новые фичи добирались до пользователей быстро и безопасно.",
    },
    skills: {
      eyebrow: "Стек",
      title: "Навыки и инструменты",
      description:
        "Работаю в экосистеме Python, оркестрирую сервисы с помощью cloud-native инструментов и современных DevOps практик.",
    },
    projects: {
      eyebrow: "Избранное",
      title: "Проекты",
    },
    contact: {
      eyebrow: "На связи",
      title: "Контакты",
      description:
        "Напишите, если нужен бэкенд-инженер для надёжных сервисов или есть идея для совместного проекта.",
      labels: {
        email: "Email",
        github: "GitHub",
        linkedin: "LinkedIn",
        telegram: "Telegram",
      },
    },
    footer: {
      note: "© 2025 Rexileer. Открыт к удалённым предложениям.",
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
    "Redis",
    "Celery",
    "Docker",
    "Docker Compose",
    "Kubernetes (basic)",
    "Nginx",
    "Grafana",
    "Prometheus",
    "GitHub Actions",
  ],
  ru: [
    "Python",
    "Django",
    "FastAPI",
    "PostgreSQL",
    "SQLAlchemy",
    "Redis",
    "Celery",
    "Docker",
    "Docker Compose",
    "Kubernetes (база)",
    "Nginx",
    "Grafana",
    "Prometheus",
    "GitHub Actions",
  ],
};

const projects = [
  {
    id: "scalping-bot",
    meta: { en: "Live Demo", ru: "Демо" },
    title: {
      en: "Crypto Scalping Bot",
      ru: "Крипто скальпинг-бот",
    },
    description: {
      en: "High-frequency trading bot with FastAPI control panel, streaming market data via WebSockets, and Redis-backed task queue for strategy execution.",
      ru: "Бот для высокочастотного трейдинга с панелью управления на FastAPI, стримингом рыночных данных через WebSocket и очередью задач на Redis для исполнения стратегий.",
    },
    tags: ["FastAPI", "Redis", "Celery", "Docker", "Prometheus"],
    links: [
      {
        type: "demo",
        href: "https://scalper.rexileer.dev",
        label: { en: "Open demo", ru: "Открыть демо" },
      },
      {
        type: "github",
        href: "https://github.com/rexileer/scalping-bot",
        label: { en: "GitHub", ru: "GitHub" },
      },
    ],
  },
  {
    id: "task-manager",
    meta: { en: "Featured", ru: "Витрина" },
    title: {
      en: "Async Task Manager",
      ru: "Асинхронный таск-менеджер",
    },
    description: {
      en: "Task management web app with Django backend, Celery workers, and real-time progress updates via Channels and Redis.",
      ru: "Веб-приложение для управления задачами: бэкенд на Django, асинхронные воркеры Celery и онлайн-обновления статуса через Channels и Redis.",
    },
    tags: ["Django", "Celery", "Redis", "Docker Compose"],
    links: [
      {
        type: "github",
        href: "https://github.com/rexileer/task-manager",
        label: { en: "GitHub", ru: "GitHub" },
      },
    ],
  },
  {
    id: "analytics-api",
    meta: { en: "API", ru: "API" },
    title: {
      en: "Usage Analytics API",
      ru: "API аналитики использования",
    },
    description: {
      en: "Observability-friendly analytics service on FastAPI with PostgreSQL, tuned for event ingestion, aggregation jobs, and Grafana dashboards.",
      ru: "Сервис аналитики на FastAPI и PostgreSQL, оптимизированный для приёма событий, агрегирующих джобов и дашбордов в Grafana.",
    },
    tags: ["FastAPI", "PostgreSQL", "SQLAlchemy", "Grafana"],
    links: [
      {
        type: "github",
        href: "https://github.com/rexileer/analytics-api",
        label: { en: "GitHub", ru: "GitHub" },
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
  return key.split(".").reduce((acc, part) => (acc ? acc[part] : undefined), copy[lang]);
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


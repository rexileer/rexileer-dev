const fallbackCopy = {
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
        "I turn rough product ideas into production-ready backend systems, bots, dashboards, and automation workflows.",
      ctaProjects: "See projects",
      ctaContact: "Let's connect",
    },
    about: {
      eyebrow: "Profile",
      title: "Short intro",
      paragraph1:
        "I build Django, FastAPI, Telegram, and data-processing systems with clean deployment and practical admin tooling.",
      paragraph2:
        "This portfolio is managed from Django admin: projects can be drafted, expanded with AI, enriched with media, and published.",
    },
    skills: {
      eyebrow: "Stack",
      title: "Skills & tools",
      description:
        "Core stack for backend systems, bots, automation, integrations, and deploy pipelines.",
    },
    projects: { eyebrow: "Selected Work", title: "Projects" },
    contact: {
      eyebrow: "Let's Talk",
      title: "Contact",
      description:
        "Reach out if you need a backend engineer for production systems, Telegram automation, or internal tools.",
      labels: {
        email: "Email",
        github: "GitHub",
        linkedin: "LinkedIn",
        telegram: "Telegram",
      },
    },
    footer: { note: " 2026 Rexileer. Available for remote opportunities." },
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
      eyebrow: "Backend-разработчик",
      title: "Создаю надежные backend-системы на Python.",
      subtitle:
        "Превращаю идеи в production-ready сервисы, Telegram-ботов, CRM, админки и автоматизацию.",
      ctaProjects: "Смотреть проекты",
      ctaContact: "Связаться",
    },
    about: {
      eyebrow: "Профиль",
      title: "Коротко обо мне",
      paragraph1:
        "Разрабатываю Django, FastAPI, Telegram и data-processing системы с понятным деплоем и удобными админками.",
      paragraph2:
        "Это портфолио управляется из Django admin: проекты можно создавать как черновики, расширять через ИИ, добавлять медиа и публиковать.",
    },
    skills: {
      eyebrow: "Стек",
      title: "Навыки и инструменты",
      description:
        "Основной стек для backend-систем, ботов, автоматизации, интеграций и деплоя.",
    },
    projects: { eyebrow: "Избранное", title: "Проекты" },
    contact: {
      eyebrow: "На связи",
      title: "Контакты",
      description:
        "Пишите, если нужен backend-разработчик для production-сервисов, Telegram-автоматизации или внутренних инструментов.",
      labels: {
        email: "Email",
        github: "GitHub",
        linkedin: "LinkedIn",
        telegram: "Telegram",
      },
    },
    footer: { note: " 2026 Rexileer. Открыт к удаленным предложениям." },
  },
};

let copy = structuredClone(fallbackCopy);
let skills = { en: [], ru: [] };
let projects = [];

const storageKey = "rexileer.lang";
const langToggle = document.getElementById("lang-toggle");
const langDisplay = document.querySelector("[data-lang-display]");
const skillsList = document.getElementById("skills-list");
const projectGrid = document.getElementById("project-grid");
const i18nElements = [...document.querySelectorAll("[data-i18n]")];

function getNestedCopy(lang, key) {
  return key
    .split(".")
    .reduce((acc, part) => (acc ? acc[part] : undefined), copy[lang]);
}

function text(value, lang) {
  if (!value) return "";
  if (typeof value === "string") return value;
  return value[lang] || value.en || value.ru || "";
}

function updateStaticText(lang) {
  i18nElements.forEach((node) => {
    const value = getNestedCopy(lang, node.dataset.i18n);
    if (typeof value === "string") node.textContent = value;
  });
}

function renderSkills(lang) {
  skillsList.innerHTML = "";
  const items = skills[lang]?.length ? skills[lang] : ["Python", "Django", "Docker"];
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    skillsList.appendChild(li);
  });
}

function createMedia(project, lang) {
  const coverUrl = project.cover?.url;
  const firstMedia = project.media?.[0];
  const media = document.createElement("div");
  media.className = "project-card-media";

  if (coverUrl) {
    const image = document.createElement("img");
    image.src = coverUrl;
    image.alt = text(project.cover.alt, lang) || text(project.title, lang);
    media.appendChild(image);
  } else if (firstMedia?.url && firstMedia.type !== "video") {
    const image = document.createElement("img");
    image.src = firstMedia.thumbnailUrl || firstMedia.url;
    image.alt = text(firstMedia.caption, lang) || text(project.title, lang);
    media.appendChild(image);
  } else {
    media.classList.add("empty");
    media.textContent = text(project.title, lang).slice(0, 2).toUpperCase();
  }

  return media;
}

function createLinkElement(link, lang) {
  const anchor = document.createElement("a");
  anchor.className = "project-link";
  anchor.href = link.href;
  anchor.target = "_blank";
  anchor.rel = "noreferrer";
  anchor.textContent = text(link.label, lang) || link.type;
  return anchor;
}

function renderProjects(lang) {
  projectGrid.innerHTML = "";
  projects.forEach((project) => {
    const card = document.createElement("article");
    card.className = "project-card";
    card.role = "listitem";

    const body = document.createElement("div");
    body.className = "project-card-body";

    const meta = document.createElement("span");
    meta.className = "project-meta";
    meta.textContent = text(project.meta, lang);

    const title = document.createElement("h3");
    title.className = "project-title";
    title.textContent = text(project.title, lang);

    const description = document.createElement("p");
    description.className = "project-description";
    description.textContent = text(project.description, lang);

    const tags = document.createElement("div");
    tags.className = "project-tags";
    (project.tags || []).slice(0, 6).forEach((tag) => {
      const span = document.createElement("span");
      span.className = "project-tag";
      span.textContent = tag;
      tags.appendChild(span);
    });

    const actions = document.createElement("div");
    actions.className = "project-links";
    const open = document.createElement("a");
    open.className = "project-link primary-link";
    open.href = project.detailUrl || `#project/${project.id}`;
    open.textContent = lang === "ru" ? "Подробнее" : "Details";
    actions.appendChild(open);
    (project.links || []).slice(0, 2).forEach((link) => actions.appendChild(createLinkElement(link, lang)));

    body.append(meta, title, description, tags, actions);
    card.append(createMedia(project, lang), body);
    projectGrid.appendChild(card);
  });
}

function renderProjectDetail(lang) {
  const route = window.location.hash.match(/^#project\/(.+)$/);
  const existing = document.getElementById("project-detail");
  if (existing) existing.remove();
  if (!route) return;

  const project = projects.find((item) => item.id === route[1]);
  if (!project) return;

  const section = document.createElement("section");
  section.id = "project-detail";
  section.className = "project-detail";

  const back = document.createElement("a");
  back.href = "#projects";
  back.className = "project-back";
  back.textContent = lang === "ru" ? "← Все проекты" : "← All projects";

  const title = document.createElement("h2");
  title.textContent = text(project.title, lang);

  const summary = document.createElement("p");
  summary.className = "project-detail-summary";
  summary.textContent = text(project.detail, lang) || text(project.description, lang);

  const grid = document.createElement("div");
  grid.className = "project-detail-grid";
  [
    [lang === "ru" ? "Задача" : "Problem", project.sections?.problem],
    [lang === "ru" ? "Решение" : "Solution", project.sections?.solution],
    [lang === "ru" ? "Результат" : "Result", project.sections?.result],
  ].forEach(([heading, value]) => {
    const content = text(value, lang);
    if (!content) return;
    const item = document.createElement("div");
    item.className = "project-detail-block";
    const h3 = document.createElement("h3");
    h3.textContent = heading;
    const p = document.createElement("p");
    p.textContent = content;
    item.append(h3, p);
    grid.appendChild(item);
  });

  const gallery = document.createElement("div");
  gallery.className = "project-gallery";
  (project.media || []).forEach((item) => {
    const figure = document.createElement("figure");
    if (item.type === "video") {
      const video = document.createElement("video");
      video.src = item.url;
      video.controls = true;
      video.preload = "metadata";
      figure.appendChild(video);
    } else {
      const image = document.createElement("img");
      image.src = item.url;
      image.alt = text(item.caption, lang) || text(item.title, lang);
      figure.appendChild(image);
    }
    const caption = text(item.caption, lang);
    if (caption) {
      const figcaption = document.createElement("figcaption");
      figcaption.textContent = caption;
      figure.appendChild(figcaption);
    }
    gallery.appendChild(figure);
  });

  const meta = document.createElement("div");
  meta.className = "project-detail-meta";
  [project.year, text(project.role, lang), ...(project.tags || [])].filter(Boolean).forEach((item) => {
    const span = document.createElement("span");
    span.textContent = item;
    meta.appendChild(span);
  });

  section.append(back, title, meta, summary, grid, gallery);
  document.querySelector("main").insertBefore(section, document.getElementById("contact"));
  section.scrollIntoView({ behavior: "smooth", block: "start" });
}

function updateLanguage(lang) {
  document.documentElement.lang = lang;
  if (langDisplay) langDisplay.textContent = lang.toUpperCase();
  updateStaticText(lang);
  renderSkills(lang);
  renderProjects(lang);
  renderProjectDetail(lang);
  localStorage.setItem(storageKey, lang);
}

function initLanguage() {
  const saved = localStorage.getItem(storageKey);
  if (saved && copy[saved]) return saved;
  return navigator.language?.startsWith("ru") ? "ru" : "en";
}

function deepMerge(target, source) {
  if (!source || typeof source !== "object") return;
  Object.keys(source).forEach((key) => {
    if (source[key] && typeof source[key] === "object" && !Array.isArray(source[key])) {
      target[key] = target[key] || {};
      deepMerge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  });
}

function applySiteData(data) {
  if (data.copy?.en) deepMerge(copy.en, data.copy.en);
  if (data.copy?.ru) deepMerge(copy.ru, data.copy.ru);
  if (data.skills?.en?.length) skills.en = data.skills.en;
  if (data.skills?.ru?.length) skills.ru = data.skills.ru;
  if (Array.isArray(data.projects)) projects = data.projects;
}

function init() {
  const lang = initLanguage();
  updateLanguage(lang);
  langToggle?.addEventListener("click", () => {
    updateLanguage(document.documentElement.lang === "en" ? "ru" : "en");
  });
  window.addEventListener("hashchange", () => updateLanguage(document.documentElement.lang));
}

document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/site-data/")
    .then((response) => (response.ok ? response.json() : Promise.reject()))
    .then((data) => {
      applySiteData(data);
      init();
    })
    .catch(() => init());
});

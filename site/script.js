document.documentElement.classList.add("js");

const app = document.getElementById("app");
const header = document.querySelector("[data-header]");
const menuToggle = document.querySelector(".menu-toggle");
const siteNav = document.querySelector(".site-nav");

let projects = [];

const escapeHTML = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const truncate = (value, length = 190) => {
  if (!value || value.length <= length) return value || "";
  return `${value.slice(0, length).trim()}…`;
};

const projectTitle = (project) => project.title?.ru || project.title?.en || project.id;
const projectDescription = (project) => project.description?.ru || project.description?.en || "";
const projectText = (field) => field?.ru || field?.en || "";

const tagsMarkup = (tags = [], limit = 5) =>
  tags
    .slice(0, limit)
    .map((tag) => `<span class="tag">${escapeHTML(tag)}</span>`)
    .join("");

const imageMarkup = (project, eager = false) => {
  const url = project.cover?.url;
  if (!url) return "";
  const alt = projectText(project.cover.alt) || projectTitle(project);
  return `<img src="${escapeHTML(url)}" alt="${escapeHTML(alt)}" loading="${eager ? "eager" : "lazy"}" decoding="async" onerror="this.remove()" />`;
};

function caseCard(project, index, eager = false) {
  return `
    <a class="case-card" href="/projects/${encodeURIComponent(project.id)}/" data-reveal>
      <div class="case-media">
        ${imageMarkup(project, eager)}
        <span class="case-index">${String(index + 1).padStart(2, "0")}</span>
        <span class="case-arrow" aria-hidden="true">↗</span>
      </div>
      <div class="case-body">
        <p class="case-meta">${escapeHTML(project.client || projectText(project.meta))} · ${escapeHTML(project.year || "проект")}</p>
        <h3 class="case-title">${escapeHTML(projectTitle(project))}</h3>
        <p class="case-description">${escapeHTML(truncate(projectDescription(project), 205))}</p>
        <div class="tag-list">${tagsMarkup(project.tags, 5)}</div>
      </div>
    </a>`;
}

function contactSection() {
  return `
    <section class="section contact-section shell" id="contact">
      <div class="contact-card" data-reveal>
        <p class="eyebrow">Есть задача или идея?</p>
        <h2>Давайте соберём <span>работающее решение.</span></h2>
        <div class="contact-links">
          <a class="button primary" href="https://t.me/rexileer" target="_blank" rel="noreferrer">Написать в Telegram <span>↗</span></a>
          <a class="button" href="mailto:rexileer@mail.ru">rexileer@mail.ru <span>↗</span></a>
        </div>
      </div>
    </section>`;
}

function renderHome() {
  const cases = projects.filter((project) => project.featured);
  const additional = projects.filter((project) => !project.featured);
  const selected = cases.slice(0, 6);

  document.title = "Rexileer — backend-системы и автоматизация";
  app.innerHTML = `
    <section class="hero">
      <div class="shell hero-copy" data-reveal>
        <p class="eyebrow">Backend · AI · Automation</p>
        <h1 class="display-title">Сложные процессы — в <em>понятные продукты.</em></h1>
        <p class="hero-lead">Проектирую и запускаю CRM, Telegram-сервисы, AI-интеграции и высоконагруженные backend-системы — от бизнес-задачи до работающего продукта.</p>
        <div class="hero-actions">
          <a class="button primary" href="#cases">Смотреть кейсы <span>↓</span></a>
          <a class="button" href="https://t.me/rexileer" target="_blank" rel="noreferrer">Обсудить проект <span>↗</span></a>
        </div>
      </div>
      <div class="shell hero-bottom" data-reveal>
        <div class="hero-proof">
          <span>Фокус</span>
          <strong>Не просто пишу код — собираю рабочий контур продукта.</strong>
        </div>
        <div class="hero-stat"><b>${projects.length}</b><span>проектов в реестре</span></div>
        <div class="hero-stat"><b>${cases.length}</b><span>подробных кейсов</span></div>
        <div class="hero-stat"><b>5+</b><span>предметных областей</span></div>
      </div>
    </section>

    <div class="client-strip" aria-label="Направления работы">
      <div class="marquee">
        ${[0, 1].map(() => `<div class="marquee-set" aria-hidden="${_escapeBool(true)}"><span>CRM и внутренние системы</span><span>Telegram-продукты</span><span>AI и RAG</span><span>Парсинг и данные</span><span>Realtime-сервисы</span><span>Платежи и подписки</span></div>`).join("")}
      </div>
    </div>

    <section class="section shell" id="cases">
      <div class="section-head" data-reveal>
        <div>
          <p class="eyebrow">Основные кейсы</p>
          <h2 class="section-title">Работа, которую можно разобрать по слоям.</h2>
        </div>
        <p class="section-intro">У каждого основного проекта есть отдельная страница: контекст, задача, решение, архитектурный вклад и практический результат.</p>
      </div>
      <div class="case-grid">${selected.map((project, index) => caseCard(project, index, index < 2)).join("")}</div>
      <div class="section-action"><a class="button" href="/projects/">Все ${cases.length} основных кейсов <span>→</span></a></div>
    </section>

    <section class="section expertise">
      <div class="shell">
        <div class="section-head" data-reveal>
          <div><p class="eyebrow">Чем могу помочь</p><h2 class="section-title">От автоматизации до продуктового backend.</h2></div>
          <p class="section-intro">Подбираю архитектуру под задачу и ограничения, а не под модный стек. В результате бизнес получает управляемую систему, а не набор разрозненных сервисов.</p>
        </div>
        <div class="expertise-grid" data-reveal>
          <article class="expertise-item"><span class="expertise-number">01</span><div class="expertise-icon">⌘</div><h3>Бизнес-системы</h3><p>CRM, внутренние кабинеты, документооборот, роли, процессы, отчётность и эксплуатационная админка.</p></article>
          <article class="expertise-item"><span class="expertise-number">02</span><div class="expertise-icon">◎</div><h3>AI и данные</h3><p>RAG, LLM-scoring, интеллектуальный поиск, парсинг, очереди обработки и интеграции внешних источников.</p></article>
          <article class="expertise-item"><span class="expertise-number">03</span><div class="expertise-icon">↗</div><h3>Telegram-продукты</h3><p>Платежи, подписки, корпоративные сценарии, лидогенерация и удобный пользовательский UX поверх серьёзного backend.</p></article>
        </div>
      </div>
    </section>

    <section class="section shell">
      <div class="process-grid">
        <div class="process-sticky" data-reveal><p class="eyebrow">Как работаю</p><h2 class="section-title">Понятный путь до запуска.</h2></div>
        <div class="process-list">
          <article class="process-step" data-reveal><span>01</span><div><h3>Погружаюсь в процесс</h3><p>Разбираю реальную задачу, пользователей, ограничения и точки, где бизнес теряет время или контроль.</p></div></article>
          <article class="process-step" data-reveal><span>02</span><div><h3>Проектирую решение</h3><p>Фиксирую границы, доменную модель, интеграции, риски и короткий маршрут к первой работающей версии.</p></div></article>
          <article class="process-step" data-reveal><span>03</span><div><h3>Собираю и показываю</h3><p>Работаю итерациями: функциональность можно проверить раньше, чем проект превратится в большой и дорогой релиз.</p></div></article>
          <article class="process-step" data-reveal><span>04</span><div><h3>Запускаю и поддерживаю</h3><p>Контейнеризация, CI/CD, логи и административные инструменты закладываются как часть продукта.</p></div></article>
        </div>
      </div>
    </section>

    <section class="section shell">
      <div class="archive-teaser" data-reveal>
        <p class="eyebrow">Полный реестр</p>
        <h2>Ещё ${additional.length} проектов — коротко и по делу.</h2>
        <p>Коммерческие задачи, тестовые проекты и собственные эксперименты: парсеры, платежи, e-commerce, blockchain scoring и небольшие CRM.</p>
        <a class="button" href="/work/">Открыть все работы <span>→</span></a>
      </div>
    </section>

    ${contactSection()}`;
}

function _escapeBool(value) {
  return value ? "true" : "false";
}

function renderCasesCatalog() {
  const cases = projects.filter((project) => project.featured);
  document.title = "Основные проекты — Rexileer";
  app.innerHTML = `
    <section class="page-hero shell">
      <p class="eyebrow" data-reveal>Основные проекты <span class="page-count">${cases.length}</span></p>
      <h1 class="display-title" data-reveal>Кейсы с контекстом, решениями и результатом.</h1>
      <p class="page-lead" data-reveal>Проекты, по которым собраны полноценные материалы. Внутри — не только стек, но и логика решения: зачем оно понадобилось, как устроено и какую работу закрывает.</p>
    </section>
    <section class="section shell">
      <div class="catalog-grid">${cases.map((project, index) => caseCard(project, index, index < 2)).join("")}</div>
    </section>
    ${contactSection()}`;
}

const sourceLabel = {
  BOTTEC: "Коммерческие",
  "Сторонние и ТЗ": "Тестовые и сторонние",
  "Пет-проекты": "Собственные",
};

function workRow(project, index) {
  const link = project.links?.[0];
  return `
    <article class="work-row" data-source="${escapeHTML(project.sourceGroup)}" data-reveal>
      <span class="work-index">${String(index + 1).padStart(2, "0")}</span>
      <h2>${escapeHTML(projectTitle(project))}</h2>
      <p>${escapeHTML(truncate(projectDescription(project), 190))}</p>
      <span class="work-stack">${escapeHTML((project.tags || []).slice(0, 4).join(" · "))}</span>
      ${link ? `<a class="work-link" href="${escapeHTML(link.href)}" target="_blank" rel="noreferrer" aria-label="Открыть репозиторий ${escapeHTML(projectTitle(project))}">↗</a>` : "<span></span>"}
    </article>`;
}

function renderWork() {
  const additional = projects.filter((project) => !project.featured);
  const groups = [...new Set(additional.map((project) => project.sourceGroup))];
  document.title = "Все работы — Rexileer";
  app.innerHTML = `
    <section class="page-hero shell">
      <p class="eyebrow" data-reveal>Дополнительные проекты <span class="page-count">${additional.length}</span></p>
      <h1 class="display-title" data-reveal>Широкая практика. Без лишней упаковки.</h1>
      <p class="page-lead" data-reveal>Здесь собраны остальные работы из реестра: компактно, с задачей, стеком и ссылкой на исходники там, где репозиторий доступен.</p>
    </section>
    <section class="section shell">
      <div class="work-toolbar" data-reveal>
        <div class="filter-list">
          <button class="filter-button active" type="button" data-filter="all">Все</button>
          ${groups.map((group) => `<button class="filter-button" type="button" data-filter="${escapeHTML(group)}">${escapeHTML(sourceLabel[group] || group)}</button>`).join("")}
        </div>
        <span class="work-total">Показано: <b data-work-count>${additional.length}</b></span>
      </div>
      <div class="work-list">${additional.map(workRow).join("")}</div>
    </section>
    ${contactSection()}`;

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-filter]").forEach((item) => item.classList.toggle("active", item === button));
      let visible = 0;
      document.querySelectorAll(".work-row").forEach((row) => {
        const show = button.dataset.filter === "all" || row.dataset.source === button.dataset.filter;
        row.hidden = !show;
        if (show) visible += 1;
      });
      document.querySelector("[data-work-count]").textContent = visible;
    });
  });
}

function fact(label, value) {
  if (!value) return "";
  return `<div class="project-fact"><span>${escapeHTML(label)}</span><b>${escapeHTML(value)}</b></div>`;
}

function storyBlock(index, label, heading, content) {
  if (!content) return "";
  return `
    <article class="story-block" data-reveal>
      <div class="story-label">${String(index).padStart(2, "0")} · ${escapeHTML(label)}</div>
      <div class="story-content"><h2>${escapeHTML(heading)}</h2><p>${escapeHTML(content)}</p></div>
    </article>`;
}

function renderProject(project) {
  if (!project || !project.featured) {
    renderNotFound();
    return;
  }
  const cases = projects.filter((item) => item.featured);
  const index = cases.findIndex((item) => item.id === project.id);
  const next = cases[(index + 1) % cases.length];
  const repository = project.links?.[0];
  const gallery = project.media || [];
  const role = projectText(project.role);

  document.title = `${projectTitle(project)} — Rexileer`;
  app.innerHTML = `
    <article>
      <header class="project-hero shell">
        <a class="project-back" href="/projects/"><span>←</span> Все основные проекты</a>
        <div class="project-heading">
          <div><p class="eyebrow">Кейс ${String(index + 1).padStart(2, "0")} / ${String(cases.length).padStart(2, "0")}</p><h1>${escapeHTML(projectTitle(project))}</h1></div>
          <div class="project-heading-side"><p>${escapeHTML(projectDescription(project))}</p>${repository ? `<a class="button" href="${escapeHTML(repository.href)}" target="_blank" rel="noreferrer">Репозиторий <span>↗</span></a>` : ""}</div>
        </div>
      </header>
      <div class="project-cover" data-reveal>${imageMarkup(project, true)}<span class="project-cover-label">${escapeHTML(project.client || "Проект")}</span></div>
      <section class="project-intro shell">
        <div class="project-facts" data-reveal>
          ${fact("Год", project.year)}
          ${fact("Заказчик / тип", project.client)}
          ${fact("Состояние", project.projectState)}
          ${fact("Роль", role)}
        </div>
        <p class="project-summary" data-reveal>${escapeHTML(projectText(project.detail) || projectDescription(project))}</p>
      </section>
      <section class="project-story shell">
        ${storyBlock(1, "Контекст", "Что требовалось решить", projectText(project.sections?.problem))}
        ${storyBlock(2, "Решение", "Как устроен продукт", projectText(project.sections?.solution))}
        ${storyBlock(3, "Результат", "Что получил проект", projectText(project.sections?.result))}
        ${project.highlights?.length ? `<article class="story-block" data-reveal><div class="story-label">04 · В фокусе</div><div class="story-content"><h2>Ключевые части системы</h2><div class="highlight-grid">${project.highlights.map((item, i) => `<div class="highlight-item"><span>${String(i + 1).padStart(2, "0")}</span><p>${escapeHTML(item)}</p></div>`).join("")}</div></div></article>` : ""}
        <article class="story-block" data-reveal><div class="story-label">05 · Стек</div><div class="story-content"><h2>Технологический контур</h2><div class="tag-list">${tagsMarkup(project.tags, 20)}</div></div></article>
        ${gallery.length ? `<div class="project-gallery">${gallery.map((item) => `<figure data-reveal>${item.type === "video" ? `<video src="${escapeHTML(item.url)}" controls preload="metadata"></video>` : `<img src="${escapeHTML(item.url)}" alt="${escapeHTML(projectText(item.caption) || projectTitle(project))}" loading="lazy" />`}<figcaption>${escapeHTML(projectText(item.caption))}</figcaption></figure>`).join("")}</div>` : ""}
      </section>
      <nav class="project-next shell" aria-label="Следующий кейс" data-reveal><a href="/projects/${encodeURIComponent(next.id)}/"><div><span>Следующий кейс</span><strong>${escapeHTML(projectTitle(next))}</strong></div><i>→</i></a></nav>
    </article>
    ${contactSection()}`;
}

function renderNotFound() {
  document.title = "Страница не найдена — Rexileer";
  app.innerHTML = `<section class="page-hero shell"><p class="eyebrow">404</p><h1 class="display-title">Такого проекта пока нет.</h1><p class="page-lead"><a class="button primary" href="/">Вернуться на главную <span>→</span></a></p></section>`;
}

function route() {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";
  if (path === "/") renderHome();
  else if (path === "/projects") renderCasesCatalog();
  else if (path === "/work") renderWork();
  else if (path.startsWith("/projects/")) renderProject(projects.find((project) => `/projects/${project.id}` === path));
  else renderNotFound();
  setupReveals();
  window.scrollTo({ top: 0, behavior: "instant" });
}

function setupReveals() {
  const items = document.querySelectorAll("[data-reveal]");
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    items.forEach((item) => item.classList.add("revealed"));
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("revealed");
        observer.unobserve(entry.target);
      }
    }),
    { threshold: 0.08, rootMargin: "0px 0px -40px" },
  );
  items.forEach((item) => observer.observe(item));
}

function setupChrome() {
  const closeMenu = () => {
    menuToggle?.setAttribute("aria-expanded", "false");
    siteNav?.classList.remove("open");
    document.body.classList.remove("menu-open");
  };
  menuToggle?.addEventListener("click", () => {
    const open = menuToggle.getAttribute("aria-expanded") !== "true";
    menuToggle.setAttribute("aria-expanded", String(open));
    siteNav?.classList.toggle("open", open);
    document.body.classList.toggle("menu-open", open);
  });
  siteNav?.addEventListener("click", closeMenu);
  window.addEventListener("scroll", () => header?.classList.toggle("scrolled", window.scrollY > 35), { passive: true });
  document.querySelector("[data-year]").textContent = new Date().getFullYear();
}

async function init() {
  setupChrome();
  try {
    const response = await fetch("/api/site-data/", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("site data unavailable");
    const data = await response.json();
    projects = Array.isArray(data.projects) ? data.projects : [];
    route();
  } catch (error) {
    console.error(error);
    app.innerHTML = `<section class="page-hero shell"><p class="eyebrow">Сайт на обновлении</p><h1 class="display-title">Не удалось загрузить проекты.</h1><p class="page-lead">Попробуйте обновить страницу чуть позже или напишите напрямую: <a href="https://t.me/rexileer">@rexileer</a>.</p></section>`;
  }
}

init();

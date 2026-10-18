// Progressive enhancement: content, routing and language work without JavaScript.
document.documentElement.classList.add('enhanced');

const header = document.querySelector('[data-header]');
const menuToggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.site-nav');
const mobileMenu = window.matchMedia('(max-width: 980px)');
const closeMenu = () => {
  menuToggle?.setAttribute('aria-expanded', 'false');
  nav?.classList.remove('open');
  document.body.classList.remove('menu-open');
  if (nav) {
    nav.inert = mobileMenu.matches;
    if (mobileMenu.matches) nav.setAttribute('aria-hidden', 'true');
    else nav.removeAttribute('aria-hidden');
  }
};
closeMenu();
mobileMenu.addEventListener('change', closeMenu);
menuToggle?.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(open));
  nav?.classList.toggle('open', open);
  document.body.classList.toggle('menu-open', open);
  if (nav) {
    nav.inert = !open;
    if (open) nav.removeAttribute('aria-hidden');
    else nav.setAttribute('aria-hidden', 'true');
  }
  if (open) nav?.querySelector('a')?.focus();
});
nav?.addEventListener('click', (event) => {
  if (event.target.closest('a')) closeMenu();
});
window.addEventListener('scroll', () => header?.classList.toggle('scrolled', window.scrollY > 35), { passive: true });
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menuToggle?.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuToggle.focus();
  }
  if (event.key === 'Tab' && menuToggle?.getAttribute('aria-expanded') === 'true') {
    const links = [...nav.querySelectorAll('a'), menuToggle];
    const first = links[0], last = links.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }
});

const catalog = document.querySelector('[data-project-catalog]');
if (catalog) {
  const buttons = [...catalog.querySelectorAll('[data-filter]')];
  const cards = [...catalog.querySelectorAll('[data-categories]')];
  function filter(category, updateUrl = false) {
    if (!buttons.some((b) => b.dataset.filter === category)) category = 'all';
    buttons.forEach((button) => {
      const active = button.dataset.filter === category;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    cards.forEach((card) => { card.hidden = category !== 'all' && !card.dataset.categories.split(' ').includes(category); });
    const empty = catalog.querySelector('[data-filter-empty]');
    if (empty) empty.hidden = cards.some((card) => !card.hidden);
    if (updateUrl) {
      const url = new URL(location.href);
      if (category === 'all') url.searchParams.delete('category');
      else url.searchParams.set('category', category);
      history.replaceState(null, '', url);
    }
    const languageLink = document.querySelector('.language-toggle');
    if (languageLink) {
      const alternate = new URL(languageLink.href, location.origin);
      if (category === 'all') alternate.searchParams.delete('category');
      else alternate.searchParams.set('category', category);
      languageLink.setAttribute('href', alternate.pathname + alternate.search);
    }
  }
  buttons.forEach((button) => button.addEventListener('click', () => filter(button.dataset.filter, true)));
  filter(new URLSearchParams(location.search).get('category') || 'all');
}

// A finite, user-started process model. No network calls or background playback.
const processLab = document.querySelector('[data-process-lab]');
if (processLab) {
  const tabs = [...processLab.querySelectorAll('[data-scenario-tab]')];
  const panels = [...processLab.querySelectorAll('[data-scenario]')];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let selected = 0, stage = 0, phase = 'idle', timer = null;
  const clearTimer = () => { if (timer !== null) clearInterval(timer); timer = null; };
  function render() {
    const panel = panels[selected];
    const steps = [...panel.querySelectorAll('[data-lab-step]')];
    steps.forEach((button, index) => {
      button.setAttribute('aria-pressed', String(index === stage));
      button.closest('[data-lab-node]').dataset.state = index < stage ? 'done' : index === stage ? 'current' : 'waiting';
    });
    panel.querySelector('[data-lab-position]').textContent = `${processLab.dataset.stepLabel} 0${stage + 1} / 04`;
    panel.querySelector('[data-lab-detail]').textContent = steps[stage].dataset.detail;
    panel.dataset.complete = String(stage === steps.length - 1);
    const button = panel.querySelector('[data-lab-run]');
    button.textContent = phase === 'running' ? processLab.dataset.pause : phase === 'paused' ? processLab.dataset.resume : phase === 'finished' ? processLab.dataset.again : processLab.dataset.run;
  }
  function pause() {
    clearTimer();
    if (phase === 'running') { phase = 'paused'; render(); }
  }
  function selectScenario(index, focus = false) {
    clearTimer(); selected = index; stage = reduced.matches ? 3 : 0; phase = reduced.matches ? 'finished' : 'idle';
    tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(i === selected)); tab.tabIndex = i === selected ? 0 : -1; });
    panels.forEach((panel, i) => { panel.hidden = i !== selected; panel.open = i === selected; });
    render();
    if (focus) tabs[index].focus();
  }
  processLab.querySelector('[data-scenario-tabs]').hidden = false;
  processLab.classList.add('is-enhanced-lab');
  panels.forEach((panel, index) => {
    panel.setAttribute('role', 'tabpanel'); panel.setAttribute('aria-labelledby', tabs[index].id);
    panel.querySelectorAll('.lab-static-step').forEach(span => { span.hidden = true; });
    panel.querySelector('[data-lab-explanation]').hidden = false;
    panel.querySelectorAll('[data-lab-step]').forEach((button, step) => {
      button.hidden = false;
      button.addEventListener('click', () => { clearTimer(); stage = step; phase = stage === 3 ? 'finished' : 'paused'; render(); });
    });
    const run = panel.querySelector('[data-lab-run]'); run.hidden = false;
    run.addEventListener('click', () => {
      if (phase === 'running') { pause(); return; }
      if (reduced.matches) { clearTimer(); stage = 3; phase = 'finished'; render(); return; }
      if (phase !== 'paused' || stage === 3) stage = 0;
      phase = 'running'; render();
      timer = setInterval(() => { stage += 1; if (stage >= 3) { clearTimer(); phase = 'finished'; } render(); }, 1100);
    });
  });
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectScenario(index));
    tab.addEventListener('keydown', event => {
      let next = index;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault(); selectScenario(next, true);
    });
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { if (!entries[0].isIntersecting) pause(); }, { threshold: .1 }).observe(processLab);
  reduced.addEventListener('change', () => { if (reduced.matches) { pause(); stage = 3; phase = 'finished'; render(); } });
  selectScenario(0);
}

// The full image list remains native HTML without JavaScript.
document.querySelectorAll('[data-study-viewer]').forEach(viewer => {
  const frames = [...viewer.querySelectorAll('[data-study-frame]')];
  const tablist = viewer.querySelector('[data-study-tabs]');
  if (frames.length < 2) return;
  const tabs = frames.map((frame, index) => {
    const button = document.createElement('button'); button.type = 'button'; button.id = `screen-tab-${index}`;
    button.setAttribute('role', 'tab'); button.setAttribute('aria-controls', frame.id);
    const image = frame.querySelector('img');
    if (image?.srcset) {
      const thumb = document.createElement('img'); thumb.src = image.srcset.split(',')[0].trim().split(' ')[0]; thumb.alt = ''; thumb.width = 96; thumb.height = 60; thumb.loading = 'lazy'; button.append(thumb);
    }
    const label = document.createElement('span'); label.textContent = `0${index + 1} / ${frame.querySelector('figcaption strong')?.textContent || ''}`; button.append(label);
    frame.setAttribute('role', 'tabpanel'); frame.setAttribute('aria-labelledby', button.id); frame.tabIndex = 0;
    tablist.append(button); return button;
  });
  let frameTransition = null;
  const stopTransition = () => { frameTransition?.cancel(); frameTransition = null; };
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopTransition(); });
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { if (!entries[0].isIntersecting) stopTransition(); }).observe(viewer);
  function select(index, focus = false, motion = false) {
    stopTransition();
    frames.forEach((frame, i) => { frame.hidden = i !== index; });
    tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(i === index)); tab.tabIndex = i === index ? 0 : -1; });
    if (motion && !document.hidden && !matchMedia('(prefers-reduced-motion: reduce)').matches && frames[index].animate) frameTransition = frames[index].animate([{ opacity: .65 }, { opacity: 1 }], { duration: 180 });
    if (focus) tabs[index].focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => select(index, false, true));
    tab.addEventListener('keydown', event => {
      let next = index;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault(); select(next, true, true);
    });
  });
  tablist.hidden = false; viewer.classList.add('is-enhanced-viewer'); select(0);
});

const galleryLinks = [...document.querySelectorAll('[data-gallery]')];
const gallery = galleryLinks.filter((link, index, links) => links.findIndex((item) => item.href === link.href) === index);
const lightbox = document.querySelector('.lightbox');
let imageIndex = 0;
let imageOpener = null;
function showImage(index) {
  imageIndex = (index + gallery.length) % gallery.length;
  const source = gallery[imageIndex];
  const image = lightbox.querySelector('[data-lightbox-image]');
  image.src = source.href;
  image.alt = source.dataset.caption;
  lightbox.querySelector('[data-lightbox-caption]').textContent = source.dataset.caption;
  lightbox.querySelector('[data-lightbox-position]').textContent = `${imageIndex + 1} / ${gallery.length}`;
}
if (lightbox && typeof lightbox.showModal === 'function') {
  galleryLinks.forEach((link) => link.addEventListener('click', (event) => {
    event.preventDefault();
    imageOpener = link;
    showImage(gallery.findIndex((item) => item.href === link.href));
    lightbox.showModal();
    document.body.classList.add('image-open');
  }));
  lightbox.querySelector('[data-lightbox-close]').addEventListener('click', () => lightbox.close());
  lightbox.querySelector('[data-lightbox-prev]').addEventListener('click', () => showImage(imageIndex - 1));
  lightbox.querySelector('[data-lightbox-next]').addEventListener('click', () => showImage(imageIndex + 1));
  lightbox.addEventListener('click', (event) => { if (event.target === lightbox) lightbox.close(); });
  lightbox.addEventListener('close', () => {
    document.body.classList.remove('image-open');
    imageOpener?.focus({ preventScroll: true });
  });
  lightbox.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); showImage(imageIndex - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); showImage(imageIndex + 1); }
  });
}

// First-party click counters; attribution is bounded on the server.
document.addEventListener('click', (event) => {
  try {
    const target = event.target.closest('[data-event]');
    if (!target) return;
    const detail = { name: target.dataset.event, location: target.dataset.location, path: location.pathname, lang: document.documentElement.lang };
    window.dispatchEvent(new CustomEvent('rexileer:event', { detail }));
    const token = document.querySelector('meta[name="csrf-token"]')?.content;
    if (!token) return;
    const body = new FormData();
    Object.entries(detail).forEach(([key, value]) => body.append(key, value));
    body.append('csrfmiddlewaretoken', token);
    if (navigator.sendBeacon?.('/api/events/', body)) return;
    fetch('/api/events/', { method: 'POST', body, credentials: 'same-origin', keepalive: true }).catch(() => {});
  } catch { /* Counters must never interrupt a link or email action. */ }
});

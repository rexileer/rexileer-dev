// Progressive enhancement: content, routing and language work without JavaScript.
document.documentElement.classList.add('enhanced');

const header = document.querySelector('[data-header]');
const menuToggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.site-nav');
const closeMenu = () => {
  menuToggle?.setAttribute('aria-expanded', 'false');
  nav?.classList.remove('open');
  document.body.classList.remove('menu-open');
};
menuToggle?.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(open));
  nav?.classList.toggle('open', open);
  document.body.classList.toggle('menu-open', open);
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
  }
  buttons.forEach((button) => button.addEventListener('click', () => filter(button.dataset.filter, true)));
  filter(new URLSearchParams(location.search).get('category') || 'all');
}

const gallery = [...document.querySelectorAll('[data-gallery]')];
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
  gallery.forEach((link, index) => link.addEventListener('click', (event) => {
    event.preventDefault();
    imageOpener = link;
    showImage(index);
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

// Lightweight first-party events. No third-party scripts or personal details.
document.addEventListener('click', (event) => {
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
});

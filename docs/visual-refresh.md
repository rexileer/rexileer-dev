# Author portfolio — 18 October 2026

One visual direction, retaining Django/static delivery and graphite/paper/lime.
No new frontend stack, external animation library, API or generated image.

## Composition

- The home intro is an interactive process demonstration, not live product logs.
  Payment/access, collection and document answers come from existing case workflows.
  Inputs, four stages, explanations, outputs and the related case change together.
  Run is finite and user-started; every stage can be selected manually.
- MeatBot, Avito and Bitrix24 immediately follow the intro. Three editorial case
  spreads use existing complete interface images, task/contribution/implemented
  workflow summaries, image enlargement and case links. No new business outcomes
  or acceptance claims were added. Registry facts and manual covers stay intact.
- Service rows replace the repeated home service panels. Existing-project work
  and the paid review are compact; the complete review description remains in a
  native disclosure. Scope/price/acceptance/handover copy remains in the process.
- Catalog heading is compact; filters and the first previews are visible early
  on desktop. Dense previews keep complete copy and native screenshot ratios.
- Case pages start with a concise overview and a large screen viewer. Keyboard
  accessible thumbnail tabs switch real images; the full lightbox still works.
  Without JavaScript all frames remain accessible. Features/decisions and confirmed
  flows follow as a compact project breakdown. No-media cases say Technical outline.
- Removed obsolete home/study/catalog composition rules rather than layering
  another set of overrides. Shared service/navigation/admin styles remain.

## Interaction and preservation

- Tab semantics, roving focus, arrow/Home/End keys; ordinary buttons for manual
  process stages, run/pause/resume and screen controls. Visible focus remains.
- Process timer pauses offscreen/hidden and stops at the last stage. Frame fades
  are finite and cancelled when hidden/offscreen. Reduced motion uses final
  walkthrough states and manual switching, with no playback animation.
- Native scenario disclosures, every image link, navigation, contact and case
  content remain available without JavaScript.
- Original click names/locations, privacy, attribution/retention, admin, registry
  sync, public email, main-only deployment, private key/.env and ©/year easter eggs
  retained. No schema or production secret changes in this pass.

## Verification and visual evidence

- 11 targeted local tests: home evidence/order/native walkthroughs; all26cases
  RU/EN retain their task/contribution/solution/result and original media links;
  existing public-page/SEO/override regressions. Full suite runs in CI only.
- Browser:70sitemap routes;24page/viewport combinations at1440/1280/390/320px;
  all52case pages additionally at320px. Actual innerWidth asserted, not inferred.
- Three scenarios/manual run, pause/background, keyboard/focus/ARIA, reduced
  motion, no-JS, image switching/lightbox/Escape/focus, filters/reload/RU-EN and
  menu checked. Technical requests carry the analytics exclusion header.
- Before/after captures for home/catalog/service/case at all four widths, with
  additional full-page/intro/featured captures. Full-page captures eagerly load
  existing images for the screenshot; normal visitors retain native lazy loading.
- One local lab run: cold desktop home LCP1056→572ms, CLS0.0308→0.0382;
  warm mobile CLS0, LCP76–100ms. These unthrottled local observations are not
  real-user performance measurements or commercial outcome claims.
- Existing responsive assets reused: no additional bitmap payload, 3.5KB-class
  compressed interaction script rather than a runtime/framework. Measurements
  and screenshots remain local review artifacts under `.local/qa/visual-refresh/`.
- After CI/main deployment, repeat public interactions/route/responsive checks
  and verify exact VPS SHA, health/logs, analytics/retention and key preservation.

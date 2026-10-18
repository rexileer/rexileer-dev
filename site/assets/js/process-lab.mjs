const root = document.querySelector('[data-process-lab]');
if (root) {
  const { createModel, reduceModel, counts, finishModel, accessResult, knowledgeDocument } = await import(`./lab-model.mjs${new URL(import.meta.url).search}`);
  const copy = JSON.parse(document.getElementById('lab-copy').textContent);
  const panels = [...root.querySelectorAll('[data-scenario]')];
  const tabs = [...root.querySelectorAll('[data-scenario-tab]')];
  const states = new Map(panels.map(panel => [panel.dataset.scenario, createModel(panel.dataset.scenario)]));
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let current = 0, timer = null, visible = false;
  const svgNS = 'http://www.w3.org/2000/svg';
  const text = (panel, selector, value) => { const node = panel.querySelector(selector); if (node && node.textContent !== String(value)) node.textContent = value; };
  const svg = (name, attrs = {}, value) => {
    const element = document.createElementNS(svgNS, name);
    Object.entries(attrs).forEach(([key, item]) => element.setAttribute(key, item));
    if (value !== undefined) element.textContent = value;
    return element;
  };
  function stopTimer() { if (timer !== null) clearTimeout(timer); timer = null; root.dataset.running = 'false'; }
  function pause() {
    stopTimer();
    const panel = panels[current], state = states.get(panel.dataset.scenario);
    if (state.phase === 'running') { states.set(state.kind, reduceModel(state, { type: 'pause' })); render(panel, true); }
    root.querySelectorAll('.sim-packet').forEach(packet => packet.getAnimations().forEach(animation => animation.cancel()));
  }

  function drawCollection(panel, state) {
    const network = panel.querySelector('[data-network]');
    const width = Math.max(220, network.clientWidth), height = 106;
    network.setAttribute('viewBox', `0 0 ${width} ${height}`);
    const centers = [width * .125, width * .375, width * .625, width * .875];
    const lineGroup = network.querySelector('[data-network-lines]');
    lineGroup.replaceChildren();
    for (let i = 0; i < 3; i += 1) lineGroup.append(svg('path', { d: `M${centers[i]} 53 H${centers[i + 1]}`, class: 'network-wire' }));
    centers.forEach((x, i) => lineGroup.append(svg('rect', { x: x - width * .1, y: 8, width: width * .2, height: 89, rx: 8, class: `network-zone zone-${i}` })));
    // Stable task nodes move between zones; identity and position come from jobs.
    const packetGroup = network.querySelector('[data-packets]');
    const existing = new Map([...packetGroup.children].map(node => [Number(node.dataset.id), node]));
    const offsets = { queued: 0, done: 0 };
    state.jobs.forEach(job => {
      let packet = existing.get(job.id);
      if (!packet) {
        packet = svg('g', { class: 'sim-packet', 'data-id': job.id });
        packet.append(svg('rect', { x: -8, y: -8, width: 16, height: 16, rx: 3 }), svg('text', { x: 0, y: 3, 'text-anchor': 'middle' }, String(job.id)));
        packetGroup.append(packet);
      }
      existing.delete(job.id);
      const index = job.status === 'queued' || job.status === 'done' ? offsets[job.status]++ : 0;
      const columns = width < 400 ? 2 : 3;
      const zone = job.status === 'queued' ? 1 : job.status === 'done' ? 3 : 2;
      const x = centers[zone] + (index % columns - (columns - 1) / 2) * 19;
      const y = 14 + Math.floor(index / columns) * 16;
      packet.dataset.status = job.status;
      packet.style.transform = `translate(${x}px, ${job.status === 'working' || job.status === 'error' ? 52 : y}px)`;
      packet.querySelector('text').textContent = job.status === 'error' ? '×' : String(job.id);
    });
    existing.forEach(node => node.remove());
    const count = counts(state);
    network.setAttribute('aria-label', `${copy.total}: ${state.total}; ${copy.queued}: ${count.queued}; ${copy.working}: ${count.working}; ${copy.done}: ${count.done}; ${copy.error}: ${count.error}`);
    const chart = panel.querySelector('[data-chart]');
    const w = Math.max(220, chart.clientWidth), h = 126, left = 25, right = w - 12, top = 24, bottom = 92;
    const maxTick = 2 * state.total + 3;
    const x = value => left + value / maxTick * (right - left);
    const y = value => bottom - value / state.total * (bottom - top);
    chart.setAttribute('viewBox', `0 0 ${w} ${h}`);
    chart.setAttribute('aria-label', `${copy.chartTitle}. ${copy.modelSteps}: ${state.tick}. ${copy.queued}: ${count.queued}; ${copy.done}: ${count.done}.`);
    chart.replaceChildren(svg('title', {}, copy.chartTitle));
    chart.append(svg('text', { x: left, y: 12, class: 'chart-axis-label' }, copy.tasks));
    for (const value of [0, state.total]) {
      chart.append(svg('line', { x1: left, y1: y(value), x2: right, y2: y(value), class: 'chart-grid' }), svg('text', { x: left - 7, y: y(value) + 4, 'text-anchor': 'end' }, value));
    }
    for (const tick of [0, Math.floor(maxTick / 2), maxTick]) chart.append(svg('text', { x: x(tick), y: 112, 'text-anchor': tick === 0 ? 'start' : tick === maxTick ? 'end' : 'middle' }, tick));
    chart.append(svg('text', { x: w / 2, y: 125, 'text-anchor': 'middle', class: 'chart-axis-label' }, copy.modelSteps));
    for (const field of ['queued', 'done']) {
      const points = state.history.map(row => `${x(row.tick)},${y(row[field])}`).join(' ');
      chart.append(svg('polyline', { points, class: `chart-line chart-${field}`, 'data-series': field }));
      chart.append(svg('circle', { cx: x(state.tick), cy: y(count[field]), r: 3, class: `chart-end chart-${field}` }));
    }
    const body = panel.querySelector('[data-history]'); body.replaceChildren();
    state.history.forEach(row => { const tr = document.createElement('tr'); ['tick', 'queued', 'working', 'done', 'error'].forEach(field => { const td = document.createElement('td'); td.textContent = row[field]; tr.append(td); }); body.append(tr); });
    chart.dataset.tick = state.tick; chart.dataset.maxTick = maxTick;
  }

  function render(panel, announce = false) {
    const state = states.get(panel.dataset.scenario), action = panel.querySelector('[data-run]');
    panel.dataset.phase = state.phase;
    action.textContent = state.phase === 'running' ? copy.pause : state.phase === 'paused' ? copy.resume : state.phase === 'complete' ? copy.replay : copy.run;
    action.disabled = state.phase === 'blocked';
    panel.querySelector('[data-step]').disabled = ['blocked', 'complete'].includes(state.phase);
    let title = copy[state.phase], detail = '';
    if (state.kind === 'collection') {
      const count = counts(state);
      panel.dataset.tick = state.tick;
      text(panel, '[data-total]', state.total); text(panel, '[data-size-output]', state.total);
      panel.querySelector('[data-batch-size]').value = state.total;
      panel.querySelector('[data-fault]').checked = state.faultArmed;
      panel.querySelector('[data-fault]').disabled = state.faultUsed;
      for (const [field, value] of Object.entries(count)) panel.querySelectorAll(`[data-count="${field}"]`).forEach(node => { node.textContent = value; });
      detail = copy[state.phase === 'blocked' ? 'failureText' : state.phase === 'complete' ? 'completeText' : state.event === 'retry' ? 'retryText' : state.event === 'processing' ? 'processingText' : state.event === 'delivered' ? 'deliveredText' : 'readyText'];
      if (state.phase === 'running') title = `${copy.done}: ${count.done} / ${state.total}`;
      const output = panel.querySelector('[data-output-records]'); output.replaceChildren();
      const jobs = state.jobs.filter(job => job.status === 'done');
      if (!jobs.length) { const p = document.createElement('p'); p.className = 'records-empty'; p.textContent = copy.emptyRecords; output.append(p); }
      else {
        const heading = document.createElement('small'); heading.textContent = copy.demoRecords; output.append(heading);
        jobs.slice(0, 3).forEach(job => { const row = document.createElement('p'); const code = document.createElement('code'); code.textContent = `DEMO-${String(job.id).padStart(2, '0')}`; const status = document.createElement('span'); status.textContent = `✓ ${copy.done}`; row.append(code, status); output.append(row); });
        if (jobs.length > 3) { const p = document.createElement('small'); p.textContent = `${copy.moreRecords}: ${jobs.length - 3}`; output.append(p); }
      }
      panel.querySelector('[data-retry]').hidden = state.phase !== 'blocked';
      drawCollection(panel, state);
    } else if (state.kind === 'access') {
      const status = accessResult(state);
      panel.dataset.outcome = status;
      panel.querySelector('[data-confirmed]').checked = state.confirmed;
      panel.querySelector('[data-term]').value = state.expired ? 'expired' : 'valid';
      title = copy[status === 'pending' ? 'pendingAccess' : status];
      if (state.phase === 'running' || state.phase === 'paused') title = copy[state.phase];
      detail = `${copy.payment}: ${state.confirmed ? copy.confirmed : copy.notConfirmed}. ${copy.term}: ${state.expired ? copy.expiredTerm : copy.validTerm}.`;
      text(panel, '[data-payment-state]', state.confirmed ? `✓ ${copy.confirmed}` : copy.notConfirmed);
      text(panel, '[data-term-state]', state.expired ? `× ${copy.expiredTerm}` : copy.validTerm);
      text(panel, '[data-invite-state]', status === 'active' ? `✓ ${copy.active}` : status === 'expired' ? `× ${copy.expired}` : copy.noInvite);
      text(panel, '[data-access-title]', copy[status === 'pending' ? 'pendingAccess' : status]);
      text(panel, '[data-invite-code]', status === 'active' ? copy.demoInvite : status === 'expired' ? copy.inactiveInvite : copy.noInvite);
      panel.querySelectorAll('.access-path > div').forEach((node, index) => { node.dataset.active = String(state.stage >= index + 1); });
    } else {
      const found = knowledgeDocument(state);
      panel.dataset.outcome = !state.checked ? 'pending' : found === null ? 'insufficient' : 'answered';
      panel.querySelector('[data-question]').value = state.question;
      panel.querySelector('[data-source]').checked = state.source;
      text(panel, '[data-question-text]', copy.questions[state.question]);
      panel.querySelectorAll('[data-document]').forEach((node, index) => { node.dataset.match = String((state.checked || state.stage >= 2) && found === index); node.dataset.connected = String(state.source); });
      title = state.checked ? found === null ? copy.insufficient : copy.answer : state.phase === 'running' || state.phase === 'paused' ? copy[state.phase] : copy.pendingAnswer;
      detail = state.checked && found !== null ? `${copy.found}: ${copy.documents[found].title}` : copy.templateNote;
      text(panel, '[data-answer]', !state.checked ? copy.pendingAnswer : found === null ? copy.insufficientText : copy.documents[found].text);
      panel.querySelector('[data-answer]').hidden = !state.checked;
    }
    text(panel, '[data-result-title]', title); text(panel, '[data-result-detail]', detail);
    if (announce) text(panel, '[data-announcement]', `${title}. ${detail}`);
  }

  function schedule() {
    stopTimer();
    const panel = panels[current], state = states.get(panel.dataset.scenario);
    if (state.phase !== 'running') return;
    if (reduced.matches) { states.set(state.kind, finishModel(state)); render(panel, true); return; }
    if (document.hidden || !visible) { pause(); return; }
    root.dataset.running = 'true';
    timer = setTimeout(() => {
      timer = null;
      const previous = states.get(state.kind);
      if (previous.phase !== 'running') return;
      const next = reduceModel(previous, { type: 'tick' }); states.set(state.kind, next);
      render(panel, next.phase !== previous.phase); schedule();
    }, 600);
  }
  function dispatch(panel, action) {
    stopTimer();
    const previous = states.get(panel.dataset.scenario);
    const base = ['input', 'size'].includes(action.type) ? reduceModel(previous, { type: 'pause' }) : previous;
    states.set(base.kind, reduceModel(base, action)); render(panel, action.type !== 'fault');
    schedule();
  }
  function choose(index, focus = false) {
    pause(); current = index;
    panels.forEach((panel, i) => { panel.hidden = i !== current; panel.open = i === current; });
    tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(i === current)); tab.tabIndex = i === current ? 0 : -1; });
    render(panels[current]); if (focus) tabs[index].focus();
  }
  panels.forEach((panel, index) => {
    panel.setAttribute('role', 'tabpanel'); panel.setAttribute('aria-labelledby', tabs[index].id);
    panel.querySelector('[data-lab-fallback]').hidden = true;
    panel.querySelector('[data-lab-interactive]').hidden = false;
    panel.querySelector('[data-run]').addEventListener('click', () => dispatch(panel, { type: states.get(panel.dataset.scenario).phase === 'running' ? 'pause' : 'start' }));
    panel.querySelector('[data-step]').addEventListener('click', () => dispatch(panel, { type: 'step' }));
    panel.querySelector('[data-reset]').addEventListener('click', () => dispatch(panel, { type: 'reset' }));
    panel.querySelector('[data-batch-size]')?.addEventListener('input', event => dispatch(panel, { type: 'size', value: event.target.value }));
    panel.querySelector('[data-fault]')?.addEventListener('change', event => dispatch(panel, { type: 'fault', value: event.target.checked }));
    panel.querySelector('[data-retry]')?.addEventListener('click', () => dispatch(panel, { type: 'retry' }));
    for (const [selector, key, convert] of [['[data-confirmed]', 'confirmed', e => e.checked], ['[data-term]', 'expired', e => e.value === 'expired'], ['[data-question]', 'question', e => Number(e.value)], ['[data-source]', 'source', e => e.checked]]) panel.querySelector(selector)?.addEventListener('change', event => dispatch(panel, { type: 'input', key, value: convert(event.target) }));
  });
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => choose(index));
    tab.addEventListener('keydown', event => {
      const next = event.key === 'ArrowRight' ? (index + 1) % tabs.length : event.key === 'ArrowLeft' ? (index - 1 + tabs.length) % tabs.length : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : null;
      if (next !== null) { event.preventDefault(); choose(next, true); }
    });
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  reduced.addEventListener('change', () => pause());
  root.querySelector('[data-scenario-tabs]').hidden = false; root.classList.add('is-enhanced-lab'); choose(0);
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { visible = entries[0].isIntersecting; if (!visible) pause(); }, { threshold: .05 }).observe(root);
  else visible = true;
  if ('ResizeObserver' in window) new ResizeObserver(() => {
    const panel = panels[current]; if (panel.dataset.scenario === 'collection') drawCollection(panel, states.get('collection'));
  }).observe(root);
}

// Deterministic teaching models. They never represent real requests or customers.
export const counts = state => {
  const value = { queued: 0, working: 0, done: 0, error: 0 };
  state.jobs.forEach(job => { value[job.status] += 1; });
  return value;
};

const snapshot = state => ({ tick: state.tick, ...counts(state) });
const record = state => ({ ...state, history: [...state.history, snapshot(state)] });
const size = value => Math.min(12, Math.max(1, Math.round(Number(value) || 1)));

export function createModel(kind, options = {}) {
  if (kind === 'collection') {
    const total = size(options.total ?? 4);
    const state = {
      kind, total, tick: 0, phase: 'ready', faultArmed: Boolean(options.faultArmed),
      faultUsed: false, event: 'ready',
      jobs: Array.from({ length: total }, (_, index) => ({ id: index + 1, status: 'queued', attempts: 0 })),
      history: [],
    };
    return record(state);
  }
  if (kind === 'access') return { kind, phase: 'ready', stage: 0, checked: false, confirmed: options.confirmed ?? false, expired: options.expired ?? false };
  return { kind: 'knowledge', phase: 'ready', stage: 0, checked: false, question: options.question ?? 0, source: options.source ?? true };
}

export function accessResult(state) {
  if (!state.checked) return 'pending';
  if (!state.confirmed) return 'unconfirmed';
  return state.expired ? 'expired' : 'active';
}

export const knowledgeDocument = state => state.source && state.question < 2 ? state.question : null;
export const modelFinished = state => ['complete', 'blocked'].includes(state.phase);

function tickCollection(state, manual) {
  if (modelFinished(state)) return state;
  const jobs = state.jobs.map(job => ({ ...job }));
  const working = jobs.find(job => job.status === 'working');
  let phase = manual ? 'paused' : 'running', event;
  let faultArmed = state.faultArmed, faultUsed = state.faultUsed;
  if (working) {
    if (faultArmed && !faultUsed) {
      working.status = 'error'; phase = 'blocked'; event = 'failure';
      faultArmed = false; faultUsed = true;
    } else {
      working.status = 'done'; event = 'delivered';
      if (jobs.every(job => job.status === 'done')) phase = 'complete';
    }
  } else {
    const queued = jobs.find(job => job.status === 'queued');
    if (!queued) return state;
    queued.status = 'working'; queued.attempts += 1; event = 'processing';
  }
  return record({ ...state, jobs, tick: state.tick + 1, phase, event, faultArmed, faultUsed });
}

export function reduceModel(state, action) {
  if (action.type === 'reset') return createModel(state.kind, state);
  if (action.type === 'pause') return state.phase === 'running' ? { ...state, phase: 'paused' } : state;
  if (action.type === 'start') {
    if (state.phase === 'blocked') return state;
    const next = state.phase === 'complete' ? createModel(state.kind, state) : state;
    return { ...next, phase: 'running' };
  }
  if (state.kind === 'collection') {
    if (action.type === 'size') return createModel('collection', { total: action.value, faultArmed: state.faultArmed });
    if (action.type === 'fault') return state.faultUsed ? state : { ...state, faultArmed: Boolean(action.value) };
    if (action.type === 'retry') {
      if (state.phase !== 'blocked') return state;
      const jobs = state.jobs.map(job => job.status === 'error' ? { ...job, status: 'queued' } : job);
      return record({ ...state, jobs, phase: 'paused', tick: state.tick + 1, event: 'retry' });
    }
    if (action.type === 'tick' || action.type === 'step') return tickCollection(state, action.type === 'step');
  } else {
    if (action.type === 'input') {
      const next = { ...state, [action.key]: action.value };
      // Once checked, these simple input rules can be re-evaluated immediately.
      if (next.checked) {
        next.phase = 'complete';
        next.stage = next.kind === 'access' ? (!next.confirmed ? 1 : next.expired ? 2 : 3) : 3;
      } else { next.phase = 'ready'; next.stage = 0; }
      return next;
    }
    if (action.type === 'tick' || action.type === 'step') {
      if (modelFinished(state)) return state;
      const stage = Math.min(3, state.stage + 1);
      const finished = stage === 3 || (state.kind === 'access' && (stage === 1 && !state.confirmed || stage === 2 && state.expired));
      return { ...state, stage, checked: finished, phase: finished ? 'complete' : action.type === 'step' ? 'paused' : 'running' };
    }
  }
  return state;
}

export function finishModel(state) {
  let next = reduceModel(state, { type: 'start' });
  // The longest supported path is 2N+3; an injected failure waits for a retry.
  for (let budget = 0; budget < 28 && !modelFinished(next); budget += 1) next = reduceModel(next, { type: 'tick' });
  return next;
}

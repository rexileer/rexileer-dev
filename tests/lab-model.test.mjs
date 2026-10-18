import test from 'node:test';
import assert from 'node:assert/strict';
import { createModel, reduceModel, counts, finishModel, accessResult, knowledgeDocument } from '../site/assets/js/lab-model.mjs';

function invariant(state) {
  const count = counts(state);
  assert.equal(Object.values(count).reduce((sum, n) => sum + n, 0), state.total);
  assert.equal(new Set(state.jobs.map(job => job.id)).size, state.total);
  assert.equal(state.history.length, state.tick + 1);
  assert.deepEqual(state.history.at(-1), { tick: state.tick, ...count });
  assert.ok(state.tick <= 2 * state.total + 3);
}

test('every supported batch finishes once with graph/counters in agreement', () => {
  for (let total = 1; total <= 12; total += 1) {
    let state = createModel('collection', { total });
    invariant(state);
    while (state.phase !== 'complete') { state = reduceModel(state, { type: 'step' }); invariant(state); }
    assert.equal(counts(state).done, total);
    assert.equal(state.tick, 2 * total);
    assert.equal(reduceModel(state, { type: 'step' }), state);
  }
});

test('a failure moves one job to error; retry retains identity and never duplicates output', () => {
  for (const total of [1, 4, 12]) {
    let state = finishModel(createModel('collection', { total, faultArmed: true }));
    invariant(state); assert.equal(state.phase, 'blocked'); assert.equal(counts(state).error, 1);
    assert.equal(finishModel(state), state);
    state = reduceModel(state, { type: 'retry' }); invariant(state);
    state = finishModel(state); invariant(state);
    assert.equal(state.phase, 'complete'); assert.equal(counts(state).done, total);
    assert.equal(state.jobs[0].attempts, 2); assert.equal(state.tick, 2 * total + 3);
  }
});

test('pause does not advance data; reset removes records and graph history', () => {
  let state = reduceModel(createModel('collection', { total: 6 }), { type: 'start' });
  state = reduceModel(state, { type: 'tick' });
  const paused = reduceModel(state, { type: 'pause' });
  assert.deepEqual(paused.jobs, state.jobs); assert.deepEqual(paused.history, state.history);
  const reset = reduceModel(paused, { type: 'reset' });
  invariant(reset); assert.equal(reset.history.length, 1); assert.equal(counts(reset).done, 0); assert.equal(reset.phase, 'ready');
});

test('new run starts a new dataset and guards the finite input range', () => {
  const complete = finishModel(createModel('collection', { total: 12 }));
  const replay = reduceModel(complete, { type: 'start' });
  assert.equal(replay.tick, 0); assert.equal(counts(replay).done, 0);
  assert.equal(createModel('collection', { total: 500 }).total, 12);
  assert.equal(createModel('collection', { total: -5 }).total, 1);
});

test('fault can be injected mid-run and is consumed exactly once', () => {
  let state = reduceModel(createModel('collection'), { type: 'step' });
  state = reduceModel(state, { type: 'fault', value: true });
  state = reduceModel(state, { type: 'step' }); assert.equal(state.phase, 'blocked');
  state = reduceModel(state, { type: 'retry' });
  assert.equal(reduceModel(state, { type: 'fault', value: true }).faultArmed, false);
  assert.equal(finishModel(state).phase, 'complete');
});

test('access depends on payment confirmation and term, not an unconditional invite', () => {
  let state = finishModel(createModel('access')); assert.equal(accessResult(state), 'unconfirmed');
  state = reduceModel(state, { type: 'input', key: 'confirmed', value: true }); assert.equal(accessResult(state), 'active');
  state = reduceModel(state, { type: 'input', key: 'expired', value: true }); assert.equal(accessResult(state), 'expired');
  state = reduceModel(state, { type: 'reset' }); assert.equal(accessResult(state), 'pending');
});

test('document answer has a matching source or explicitly has insufficient context', () => {
  let state = finishModel(createModel('knowledge')); assert.equal(knowledgeDocument(state), 0);
  state = reduceModel(state, { type: 'input', key: 'question', value: 1 }); assert.equal(knowledgeDocument(state), 1);
  state = reduceModel(state, { type: 'input', key: 'question', value: 2 }); assert.equal(knowledgeDocument(state), null);
  state = reduceModel(state, { type: 'input', key: 'question', value: 0 });
  state = reduceModel(state, { type: 'input', key: 'source', value: false }); assert.equal(knowledgeDocument(state), null);
});

test('all reductions are pure and reduced-motion finish is bounded', () => {
  const state = createModel('collection', { total: 12 }); const original = structuredClone(state);
  const next = finishModel(state); assert.equal(next.phase, 'complete'); assert.deepEqual(state, original);
  assert.equal(finishModel(createModel('access', { confirmed: true })).stage, 3);
});

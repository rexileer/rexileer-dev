# Interactive process lab

The homepage lab is a deterministic teaching example based on three existing
cases. It does not call their backends, initiate payments, issue real invitations,
query an LLM or represent customer records. RU and EN use the same model and
localized copy in `backend/core/experience.py`.

## Collection

`site/assets/js/lab-model.mjs` owns job identities, statuses, model steps and
snapshots. The controller derives packets, four counters, result records and
both chart series from that state. Every job belongs to exactly one of queued,
working, done or error; their sum is always the selected total, from 1 to 12.

A step either starts one queued job or resolves the working job. An injected
worker fault consumes one attempt and blocks the run. Restore moves the same
job back to the queue; Resume or One step processes it again without creating
another identity or duplicating its output. A run permits one injected fault.
Reset clears snapshots/results while retaining the selected inputs. Replay
creates a fresh teaching batch.

The SVG chart shows queued and completed tasks from recorded snapshots. X is
model steps, Y is tasks; the finite domain is 0…2N+3. A normal run takes 2N
steps; failure and recovery can take 2N+3. These are not seconds, throughput,
load-test data or production performance. Its expandable table contains the
same snapshots, including working/error counts.

## Access and document answer

- Access checks confirmation and then the subscription term. Unconfirmed
  payment gives no invitation; an expired term makes the demo invitation
  inactive. A confirmed, valid subscription displays plain demonstration text,
  never a usable invitation URL. Changing checked inputs recomputes the result.
- Document answer offers three fixed questions and two synthetic documents.
  The first two questions match one highlighted document and return its exact
  template text. The third question, or disabling the source, explicitly gives
  insufficient context. There is no generated unsupported answer.

## Browser behavior and accessibility

`site/assets/js/process-lab.mjs` renders the model. The module and its imported
model share the content-version query, including model changes in the version
hash, so immutable caching cannot retain an earlier model. MIME is explicit.

One finite 600ms timeout runs only after Run/Resume. Completion, a fault,
pause, reset, scene switch, a hidden document or an offscreen lab clears it.
Returning to the scene does not restart it. No background polling, intervals,
external requests or new analytics events are introduced. Reduced motion uses
a bounded instant result or manual steps, with packet transitions disabled.

Native controls, keyboard tab navigation, visible focus, text error states and
quiet completion/user-action announcements are preserved. Controls, including
recovery, precede the diagram. Without JS, native disclosures retain all three
complete four-step explanations and their real case links.

Large site surfaces in the lab, featured MeatBot spread and service audit block
now use dark colors. Real screenshots, original media, galleries and their
provenance remain unchanged. No bitmap assets were added or removed in this
follow-up; the existing image mapping remains in `asset-audit.md`.

## Verification

- `node --test tests/lab-model.test.mjs`: all 12 supported sizes, invariants,
  failure/retry, fresh replay/reset, pure updates and bounded completion.
- CI also checks all JS module syntax and runs the existing Django suite.
- Targeted local Django checks cover bilingual SSR, versioned module loading,
  explicit MIME, case facts/media and public routes. Full local suite is not run.
- Browser checks cover every collection step for 1/4/12 jobs, packet/count/
  chart/table agreement, recovery, focus, hidden/offscreen behavior, both P1
  scenes, reduced motion, native no-JS RU/EN and 1440/1280/390/320px layouts.
- Separate regression checks retain 70 sitemap routes, 52 bilingual case pages
  at 320px, catalog/filter/language/menu, galleries and first-party CTA events.
- Private QA captures are under `.local/qa/lab-v2/`: before/current lab and
  MeatBot, plus error/completion/document-answer/audit states. Timing samples
  are single unthrottled browser observations, not real-user performance claims.

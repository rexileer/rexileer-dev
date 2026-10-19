# Rexileer Desk

An owner workspace at `https://desk.rexileer.ru/`. The public portfolio and Desk
use the same repository/image but separate Django settings, URLconf, application,
database, key, account, session and container. No personal-data API is installed
in the portfolio. There is no registration, mail sending, bank integration or AI.

## Runtime boundary

- `desk_config.settings` installs auth/contenttypes/sessions/messages/desk only;
  it never imports portfolio settings, core models or analytics middleware.
- `rexileer-desk`: one Gunicorn worker, two threads, UID10001 worker,256MB memory,
  0.35CPU,64PIDs; loopback8081 maps internal8080. Separate internal Docker network.
- `desk_data` is a private SQLite volume; `desk_documents` contains immutable
  encrypted blobs. Neither is mounted in `rexileer-portfolio`.
- Private configuration stays outside checkout at `/root/rexileer-private/`.
  `desk.env` and `document.env` are separate root0600 files in a0700 directory.
  They are not build arguments, image files, Git files or backup members.
- Exact host `desk.rexileer.ru`, trusted HTTPS proxy, independent `__Host-` Secure/
  HttpOnly/Strict cookies, CSRF, safe login next, POST logout, no-store, noindex,
  CSP and frame restrictions. Only local health probing bypasses login; nginx
  blocks `/health/` externally. CSS/fonts contain no personal data.
- Login has a persisted shared eight-attempt/15minute allowance independent of
  username/client cookie, plus nginx IP rate limiting. A valid password is still
  blocked during lockout. Locks expire; there is no permanent lock.
- Desk nginx access logging is off; no POST bodies, passwords or financial
  payloads are deliberately logged. Existing proxy/system/backups elsewhere have
  independent policies. Referrer policy is same-origin so native form Origin
  remains valid; nothing is sent to external sites as referrer.

## Accounting rules

Amounts are Decimal with two decimal places, never Python floats. A task status
does not generate money. Operations are actual income/expense, require an explicit
confirmation and cannot be dated in the future. A dated expected receipt is
separate from cash. Confirmed expectations contribute only their unpaid portion;
proposals/cancelled expectations and entries without dates do not enter the
near-term summary. New income and prior-project payments have a visible filter.

Obligations have a confirmed amount **on a date**, or both are unknown. The
displayed derived amount subtracts only explicitly allocated actual principal
strictly after that snapshot date. Same-day or older operations are not
subtracted again. Unknown remains unknown. Plans and expenses without known
principal never reduce it. No interest/penalty/early-repayment calculation exists.
Plans are not added to snapshots to manufacture an overall debt figure.

Planned payments can remain unverified drafts without an amount/date. Only a
confirmed amount/date enters the calendar. Payment status and partial coverage
derive from linked actual expenses; there is no independent paid toggle.
Archiving a transaction removes it from calculations, preserves history and is
reversible. Changes serialize through a SQLite writer lock and are audited.

Source reference amounts, historical cumulative payments and uncertain deadlines
stay in metadata/notes. Historic cumulative payments without dates never become
current income. A separate non-accounting register holds rejected/pending
applications and source reminders. Source records do not imply a complete
financial inventory. Original Sheets/files are not edited or deleted.

## Documents, extra services and creditor addresses

PDF, JPEG and PNG only;10MB/file,20million image pixels,512MB total ciphertext.
Extension, declared MIME, signature/format and image validity are checked. No
Office, HTML, SVG, archives, OCR, thumbnails or preview cache. Random storage keys
are independent of original filenames. All preview/download routes check owner
authentication and host; URLs alone grant no access. Files get no-store/nosniff
and canonical safe Content-Disposition names. PDF inline delivery is sandboxed,
without scripts or same-origin privileges; a visible download fallback remains
when a browser refuses its native viewer. Images are displayed without editing
their contents. A receipt never creates another operation or closes a loan.

Encryption uses [cryptography Fernet](https://cryptography.io/en/latest/fernet/),
an authenticated standard implementation, not custom cryptography. Blobs are
Fernet tokens named `<random-uuid>.fernet`; original names, MIME, byte count and
SHA256 live in the private DB. The independently random32byte Fernet key resides
only in `document.env`/runtime, separately from DB, blobs and backups. A missing
or invalid key fails closed; the wrong valid key returns a generic unavailable
response without plaintext. Do not replace or regenerate an existing key. Key
rotation requires an explicit migration of all blobs, not an env edit.

This protects document bytes when a disk/backup is obtained without the key. It
does not protect against full compromise of the running server/process; metadata
and database records are not encrypted by Fernet. Fernet tokens expose creation
timestamps. File size limits bound memory use during authenticated decryption.

Extra services retain reported amounts/dates and verification/cancellation/refund
states. No deadline or legal basis is invented. Expected refunds are not cash;
"received" requires an existing actual income transaction. Creditor email records
contain purpose, exact supplied address, source and verification date. Letters
are plain text notes with optional related PDF/image evidence. There are no mail
credentials, mailbox connections or sending functions.

## Initial owner access

The private entrypoint runs `desk_owner --generate-file` once. It creates a
separate account `owner`; portfolio administration credentials are not copied or
changed. The generated password remains in the root-only bootstrap file
`/root/rexileer-private/bootstrap/owner-password.txt`. Deliver it only through a
private local file or password manager, never a chat/log/commit. The owner can
change it at `/password/`. Subsequent deployments do not reset the password.

If a reset is explicitly needed, supply a new private file to `desk_owner
--password-file ... --reset` inside Desk. This affects only its account. Do not
reuse the public administrator password or print environment/key files.

## Private SSH CRUD and import

Prepare a UTF-8 JSON file outside Git with mode0600. Example schema (synthetic):

```json
{"version":1,"records":[
  {"entity":"project","source":"my_source","external_id":"p-1",
   "import_batch":"snapshot-date","fields":{"name":"Example project"}},
  {"entity":"task","source":"my_source","external_id":"t-1",
   "fields":{"title":"Next step","project":{"source":"my_source","external_id":"p-1"}}}
]}
```

Entities: contact, project, task, obligation, payment, expected, transaction,
reference, addon, email, letter. Fields follow the models/forms; monetary values
are strings such as `"125.50"`, dates `YYYY-MM-DD`, unknowns JSON null. Relations
are source/external_id objects or numeric IDs. Same entity/source/external_id
updates only supplied fields; unchanged repeat creates neither duplicates nor
another audit entry. Archive through `fields:{"archived":true}`, restore with
false. The operation is atomic across the whole file, including references.

```sh
docker compose exec -T desk python manage.py desk_data import - < /root/rexileer-private/input.json
docker compose exec -T desk python manage.py desk_data import - --apply < /root/rexileer-private/input.json
docker compose exec -T desk python manage.py desk_data export --output /app/desk-db/exports/new-name.json
```

The first command is a rollback preview. CLI prints counts, not records or
secrets. The browser `/data/` offers the same validation, preview and explicit
confirmation, with signed15minute owner-bound payload. CSV uses entity/source/
external_id/import_batch columns and named field columns; relations may be quoted
JSON objects. Empty CSV cells mean omitted fields; use JSON null to clear a value.
Files are limited to2MB/1000records. New source snapshots require review; there is
no automatic bidirectional Sheets synchronization.

`desk_file upload --metadata <private-json> --file <private-file> --source ...
--external-id ...` validates/encrypts an attachment with the same service as the
UI. Default is preview with no saved file; add `--apply` to persist. `update` with
the same source/id changes metadata/archive state, never original bytes. Run file
commands as UID10001 with readable private inputs; do not expose input directories
to the portfolio. JSON export labels attachments excluded and includes metadata;
only the full backup below carries encrypted files.

## Complete private backup and restore

```sh
docker compose exec -T desk python manage.py desk_backup backup /app/desk-db/backups/new-name.desk
docker compose exec -T desk python manage.py desk_backup verify /app/desk-db/backups/new-name.desk
```

`.desk` is a strict tar bundle: a consistent SQLite snapshot, exactly its
referenced immutable ciphertext files, and an authenticated encrypted hash manifest.
The document key authenticates the DB hash as well as file hashes; a rewritten
plain manifest cannot substitute another database. No configuration or
key files are included. Verification copies to a private temporary directory,
checks archive paths/types/size, SQLite integrity, manifests and decryption hashes
using the **separate** key. No decrypted attachment is written to disk. Missing
files or wrong key reject the backup. There is a free-space guard; historical
backups are not silently removed. Copy bundles to a private external backup
location and preserve `document.env` and `desk.env` separately. Losing the document
key loses access to document bytes even if a bundle survives.

For an explicit maintenance restore, keep the key files, place the verified
bundle in the private volume, and stop **only Desk**:

```sh
docker compose stop desk
docker compose run --rm --no-deps --entrypoint python -e DESK_RESTORE_MAINTENANCE=1 desk manage.py desk_backup restore /app/desk-db/backups/chosen-name.desk --apply
docker compose up -d desk
```

Restore first verifies everything, backs up the previous working state and then
restores blobs/DB. It never replaces a conflicting immutable blob. Run health and
owner HTTPS login checks afterwards. SQLite-only backups remain a diagnostic
legacy path; use `.desk` for normal backup/restore so files are not omitted.

## Deployment and verification

Main-only existing CI/CD runs public checks and isolated Desk checks separately.
`prepare-desk.py` preserves private keys/owner and backs up existing Desk before
rebuild. The private entrypoint migrates its own DB only. `deploy-desk.sh` validates
the independent loopback health, installs only the Desk vhost, obtains its own
webroot certificate and reloads validated nginx. It neither changes other domains
nor stops portfolio for certificate issuance. Native Certbot timer renews it.

Targeted local tests and synthetic browser flows cover accounting, identity,
CSRF/cookies/next, host access, import rollback/idempotence, file types/keys/bytes,
archive and complete restore. Full suites run only in CI. Private/source data is
never shipped as fixtures or screenshots; local UI captures use a separate
synthetic database. Public portfolio routes and server invariants are rechecked
after deployment. Real addresses/documents still require supplied evidence.

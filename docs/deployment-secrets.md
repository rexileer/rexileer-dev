# Django production signing key

Production reads `DJANGO_SECRET_KEY` from the existing private server `.env`.
Keep this file owned by root with mode0600. It is ignored by Git, excluded from
the Docker build context and preserved by the main-only deployment cleanup.
Deploy does not generate or replace this persistent key.

Missing, short, repetitive or development-labelled keys stop configuration with
a generic error. There is no public/default signing key or old-key fallback.
Rotate intentionally after a private configuration/database backup: current
admin sessions and old Django signatures become invalid. User passwords,
provider credentials and the independent database AnalyticsKey do not change.
Application rollback should retain the new secure key, never re-enable the old
public default. A database restore requires checking for subsequent business edits.

CI uses a random temporary key file outside the checkout, passed only by file
path (`DJANGO_SECRET_KEY_FILE`). Docker build commands use random process-local
keys, never image ENV or persisted key files. Local offline checks can use the
same private-file interface. Never print keys or run resolved Compose/configuration
dumps into logs; validate using booleans and `docker compose config --quiet`.

# Service domains

All active sites use `.tech`:

| Host | Upstream | Access |
| --- | --- | --- |
| rexileer.tech | 127.0.0.1:8080 | Public portfolio |
| desk.rexileer.tech | 127.0.0.1:8081 | Existing single Desk owner |
| ai-leads.rexileer.tech | 127.0.0.1:8004 | Existing AI Leads login/API authorization |
| logs.rexileer.tech | 127.0.0.1:8088 | Existing nginx Basic authentication |

Each host needs an A record to `45.95.0.124`. `www` redirects to the portfolio.
No AAAA should be added until the VPS has working public IPv6 routing. The old
`app.rexileer.ru` proxy targeted port 3000 with no running application, so no
replacement app host or nonexistent service is created.

`prepare-tech-domains.sh` obtains individual webroot certificates before
restarting Desk with its new exact allowed host/origin. The main deployment then
installs the Desk, AI and logs vhosts. Certbot's existing timer and checked nginx
reload hook handle renewal. Log streaming retains authenticated WebSocket/SSE
proxying. Desk retains no-store headers, host-only Secure/HttpOnly/Strict cookies,
owner checks and independent keys/storage. Sessions do not move across browser
hostnames: log in on the new host using the unchanged password.

AI Leads is a separately maintained project with existing uncommitted changes.
`migrate-ai-tech.py` updates only five domain environment keys in its ignored
dotenv and recreates affected services without building images. Its private
temporary Compose override preserves the exact running non-domain environment,
including any values different from pending dotenv edits. Images and mounts are
checked after recreation; original source/Git changes, accounts, tokens and
databases are retained. No AI calls or notifications are triggered for QA.
The runtime override is root-only outside the checkout; never print its content.

`retire-ru-hosts.py` disables only the five known old enabled vhost symlinks and
archives the four old Certbot renewal configurations under `/root/server-fixes`.
It retains old certificate files and sites-available/history, validates nginx
before reload and restores the links if validation/reload fails. `.ru` renewal
or redirect availability is not required. The SSH port, other containers and
their ports are preserved.

Before cutover, back up nginx/Let’s Encrypt, Desk data+independent keys, AI dotenv
and active container configuration in a root-only directory. Test each new
certificate with `certbot renew --cert-name HOST --dry-run
--no-random-sleep-on-renew`. Test real owner login/logout on Desk, anonymous
denials/public isolation, AI login and existing protected logs. Keep secrets and
real financial screenshots out of Git and QA output.

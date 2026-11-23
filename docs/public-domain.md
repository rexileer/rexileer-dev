# Public portfolio domain

Canonical public origin: `https://rexileer.tech`.
Both `rexileer.tech` and `www.rexileer.tech` need A records pointing to
`45.95.0.124`. Do not publish an AAAA record until this VPS has working IPv6
routing. HTTP and HTTPS www redirect to the canonical origin and preserve the
path and query string.

The main deployment runs `ops/deploy-public.sh`. It backs up nginx, refuses to
overwrite unmanaged vhosts, validates configuration before each reload, and
restores the previous public vhost on failure. HTTP-01 uses `/var/www/acme`.
Certbot manages one certificate covering both names; `certbot.timer` renews it
and a deployment hook validates and reloads nginx. Verify renewal explicitly:

```sh
certbot renew --cert-name rexileer.tech --dry-run --no-random-sleep-on-renew
```

`ops/public-http.conf` and `ops/public-https.conf` are the active public proxy
templates. `docker/nginx.conf` is an unused historical static hosting example.
Only the public app on loopback 8080 is proxied. Closed Desk routes are absent
from its URL configuration. Public metadata, sitemap and robots use the fixed
canonical origin; request Host never determines SEO URLs. Contacts, email,
external links and author easter eggs retain their original destinations.

Desk is isolated at `https://desk.rexileer.tech`, loopback 8081, with its own
certificate and unchanged credentials, keys and volumes. AI Leads uses
`https://ai-leads.rexileer.tech`; authenticated logs use
`https://logs.rexileer.tech`. Each name needs its own A record to the VPS.
Deployment verifies each exact vhost with trusted TLS against loopback.

On 23 November 2026 the old `rexileer.ru` zone delegates to
`ns1.expired.reg.ru` / `ns2.expired.reg.ru`; public A records point elsewhere.
Some recursive caches still return the VPS for Desk, while the VPS resolver
already returns an unrelated address. Old public redirects cannot be served
reliably. The owner chose to abandon that domain. The following subdomain
migration disables old enabled vhosts and archives their renewal jobs, retaining
the configuration and certificate history. Active services depend only on
`.tech`. See [subdomains.md](subdomains.md) for the private-host cutover.

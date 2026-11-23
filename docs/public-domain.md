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

Desk remains isolated at `desk.rexileer.ru`, loopback 8081, with its existing
certificate, credentials, keys and volumes. Deployment probes that vhost with
verified TLS against loopback, independently of external DNS. This does not
repair an expired domain or guarantee external availability/renewal.

On 23 November 2026 the old `rexileer.ru` zone delegates to
`ns1.expired.reg.ru` / `ns2.expired.reg.ru`; public A records point elsewhere.
Some recursive caches still return the VPS for Desk, while the VPS resolver
already returns an unrelated address. Old public redirects cannot be served
reliably until the owner renews/restores that zone. Existing old-domain and
neighboring nginx vhosts are preserved. No `desk.rexileer.tech` host is enabled:
moving Desk requires an explicit DNS record and a separately coordinated
host/session/certificate migration.

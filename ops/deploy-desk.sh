#!/bin/sh
set -eu
cd /root/rexileer-dev
for attempt in $(seq 1 45); do
  if docker exec rexileer-desk python -c "import urllib.request; urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8080/health/',headers={'Host':'desk.rexileer.tech','X-Forwarded-Proto':'https'}))"; then
    break
  fi
  if [ "$attempt" = 45 ]; then
    docker compose logs --tail=100 desk
    exit 1
  fi
  sleep 2
done
target=/etc/nginx/sites-available/desk.rexileer.tech.conf
if [ -e "$target" ] && ! head -1 "$target" | grep -q 'Managed by rexileer-dev'; then
  echo "Existing Desk vhost is not managed by this repository; refusing to replace it." >&2
  exit 1
fi
install -d -m 0755 /var/www/acme/.well-known/acme-challenge
if [ ! -s /etc/letsencrypt/live/desk.rexileer.tech/fullchain.pem ]; then
  install -m 0644 ops/desk-http.conf "$target"
  ln -sfn "$target" /etc/nginx/sites-enabled/desk.rexileer.tech.conf
  nginx -t
  systemctl reload nginx
  certbot certonly --webroot -w /var/www/acme -d desk.rexileer.tech --cert-name desk.rexileer.tech --non-interactive --agree-tos --register-unsafely-without-email
fi
cat ops/desk-http.conf ops/desk-https.conf > "$target"
ln -sfn "$target" /etc/nginx/sites-enabled/desk.rexileer.tech.conf
nginx -t
systemctl reload nginx
https_ready=0
for attempt in $(seq 1 20); do
  # Verify this VPS's exact isolated vhost without bypassing TLS validation.
  if curl -fsS --resolve desk.rexileer.tech:443:127.0.0.1 -o /dev/null https://desk.rexileer.tech/login/; then
    https_ready=1
    break
  fi
  sleep 1
done
test "$https_ready" = 1
curl -fsS -o /dev/null http://127.0.0.1:8080/
docker compose ps

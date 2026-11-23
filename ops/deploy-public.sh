#!/bin/sh
set -eu
cd /root/rexileer-dev
target=/etc/nginx/sites-available/rexileer.tech.conf
enabled=/etc/nginx/sites-enabled/rexileer.tech.conf
if [ -e "$target" ] && ! head -1 "$target" | grep -q 'Managed by rexileer-dev: public portfolio only'; then
  echo 'Refusing to replace an unmanaged public vhost.' >&2
  exit 1
fi
umask 077
backup="/root/server-fixes/public-tech-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$backup"
tar -czf "$backup/nginx-before.tar.gz" -C /etc nginx
had_target=0
if [ -f "$target" ]; then
  cp -p "$target" "$backup/public.conf"
  had_target=1
fi
rollback() {
  if [ "$had_target" = 1 ]; then
    cp -p "$backup/public.conf" "$target"
  else
    rm -f "$enabled" "$target"
  fi
  nginx -t && systemctl reload nginx
}
trap rollback EXIT
install -d -m 0755 /var/www/acme/.well-known/acme-challenge
if [ ! -s /etc/letsencrypt/live/rexileer.tech/fullchain.pem ]; then
  install -m 0644 ops/public-http.conf "$target"
  ln -sfn "$target" "$enabled"
  nginx -t
  systemctl reload nginx
  certbot certonly --webroot -w /var/www/acme \
    -d rexileer.tech -d www.rexileer.tech --cert-name rexileer.tech \
    --non-interactive --agree-tos --register-unsafely-without-email
fi
cat ops/public-http.conf ops/public-https.conf > "$target"
chmod 0644 "$target"
ln -sfn "$target" "$enabled"
nginx -t
systemctl reload nginx
# Renewed certificates must be loaded only after validating nginx configuration.
install -d -m 0755 /etc/letsencrypt/renewal-hooks/deploy
printf '%s\n' '#!/bin/sh' 'set -eu' '/usr/sbin/nginx -t' '/bin/systemctl reload nginx' > /etc/letsencrypt/renewal-hooks/deploy/20-reload-nginx
chmod 0755 /etc/letsencrypt/renewal-hooks/deploy/20-reload-nginx
systemctl enable --now certbot.timer
systemctl is-active --quiet certbot.timer
for attempt in $(seq 1 20); do
  if curl -fsS --resolve rexileer.tech:443:127.0.0.1 -o /dev/null https://rexileer.tech/; then
    trap - EXIT
    exit 0
  fi
  sleep 1
done
exit 1

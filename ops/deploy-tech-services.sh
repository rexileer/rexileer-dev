#!/bin/sh
set -eu
cd /root/rexileer-dev
python3 ops/migrate-ai-tech.py
for host in ai-leads.rexileer.tech logs.rexileer.tech; do
  target="/etc/nginx/sites-available/$host.conf"
  if [ -e "$target" ] && ! head -1 "$target" | grep -q 'Managed by rexileer-dev'; then
    echo "Refusing to replace unmanaged vhost: $host" >&2
    exit 1
  fi
done
install -m 0644 ops/ai-leads-tech.conf /etc/nginx/sites-available/ai-leads.rexileer.tech.conf
install -m 0644 ops/logs-tech.conf /etc/nginx/sites-available/logs.rexileer.tech.conf
ln -sfn /etc/nginx/sites-available/ai-leads.rexileer.tech.conf /etc/nginx/sites-enabled/ai-leads.rexileer.tech.conf
ln -sfn /etc/nginx/sites-available/logs.rexileer.tech.conf /etc/nginx/sites-enabled/logs.rexileer.tech.conf
nginx -t
systemctl reload nginx
for attempt in $(seq 1 30); do
  code=$(curl -sS --resolve ai-leads.rexileer.tech:443:127.0.0.1 -o /dev/null -w '%{http_code}' https://ai-leads.rexileer.tech/admin/login/ || true)
  if [ "$code" = 200 ]; then break; fi
  test "$attempt" != 30
  sleep 2
done
test "$(curl -sS --resolve logs.rexileer.tech:443:127.0.0.1 -o /dev/null -w '%{http_code}' https://logs.rexileer.tech/)" = 401

#!/bin/sh
set -eu
cd /root/rexileer-dev
install -d -m 0755 /var/www/acme/.well-known/acme-challenge
for host in desk.rexileer.tech ai-leads.rexileer.tech logs.rexileer.tech; do
  if [ -s "/etc/letsencrypt/live/$host/fullchain.pem" ]; then
    continue
  fi
  target="/etc/nginx/sites-available/$host.conf"
  if [ -e "$target" ] && ! head -1 "$target" | grep -q 'Managed by rexileer-dev'; then
    echo "Refusing to replace unmanaged vhost: $host" >&2
    exit 1
  fi
  umask 077
  backup="/root/server-fixes/tech-certificate-$(date -u +%Y%m%dT%H%M%SZ)-$host"
  mkdir -p "$backup"
  tar -czf "$backup/nginx-before.tar.gz" -C /etc nginx
  cat > "$target" <<EOF
# Managed by rexileer-dev: temporary ACME vhost.
server {
    listen 80;
    listen [::]:80;
    server_name $host;
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/acme;
        try_files \$uri =404;
    }
    location / { return 301 https://$host\$request_uri; }
}
EOF
  chmod 0644 "$target"
  ln -sfn "$target" "/etc/nginx/sites-enabled/$host.conf"
  nginx -t
  systemctl reload nginx
  certbot certonly --webroot -w /var/www/acme -d "$host" --cert-name "$host" \
    --non-interactive --agree-tos --register-unsafely-without-email
done

FROM nginx:1.25-alpine

LABEL org.opencontainers.image.source="https://github.com/rexileer/portfolio"
LABEL org.opencontainers.image.description="Minimalist bilingual portfolio site served by Nginx."

RUN rm -f /etc/nginx/conf.d/default.conf

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY site /usr/share/nginx/html

EXPOSE 80
EXPOSE 443

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -q --spider http://127.0.0.1/ || exit 1



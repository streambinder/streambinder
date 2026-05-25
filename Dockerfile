FROM ghcr.io/astral-sh/uv:0.11.12 AS uv
FROM alpine:3 AS builder
WORKDIR /build
RUN apk add --no-cache bash git make minify python3
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
RUN make

FROM alpine:3
RUN apk add --no-cache lighttpd && \
    adduser -S -u 1000 streambinder && \
    mkdir -p /tmp/lighttpd-deflate && \
    chown -R streambinder /tmp/lighttpd-deflate /var/log/lighttpd
COPY docker/lighttpd.conf /etc/lighttpd/lighttpd.conf
COPY --from=builder /build/build /var/www/localhost/htdocs
RUN cp /var/www/localhost/htdocs/404/index.html /var/www/localhost/htdocs/status-404.html && \
    cp /var/www/localhost/htdocs/500/index.html /var/www/localhost/htdocs/status-500.html
USER streambinder
EXPOSE 8080
STOPSIGNAL SIGINT
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
LABEL org.opencontainers.image.source=https://github.com/streambinder/streambinder \
      org.opencontainers.image.title=streambinder \
      org.opencontainers.image.description="Personal site of Davide Pucci" \
      org.opencontainers.image.licenses=GPL-3.0

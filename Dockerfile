FROM ghcr.io/astral-sh/uv:0.11.12 AS uv
FROM alpine:3 AS builder
WORKDIR /build
RUN apk add --no-cache bash git make python3
COPY --from=uv /uv /usr/local/bin/uv
COPY . .
RUN uv sync --frozen && \
    wget -q https://github.com/tdewolff/minify/releases/download/v2.9.10/minify_linux_amd64.tar.gz && \
    tar -xvf minify*.tar.gz -C /bin && \
    make

FROM alpine:3
RUN apk add --no-cache lighttpd && \
    echo 'server.error-handler-404 = "/404"' >> /etc/lighttpd/lighttpd.conf && \
    echo 'server.port = 8080' >> /etc/lighttpd/lighttpd.conf && \
    sed -i 's|/run/lighttpd.pid|/tmp/lighttpd.pid|' /etc/lighttpd/lighttpd.conf && \
    adduser -S streambinder && \
    chown -R streambinder /var/log/lighttpd
USER streambinder
COPY --from=builder /build/build /var/www/localhost/htdocs
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
EXPOSE 8080
HEALTHCHECK CMD [ "/usr/bin/curl", "127.0.0.1" ]
LABEL org.opencontainers.image.source=https://github.com/streambinder/streambinder

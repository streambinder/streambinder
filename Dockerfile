FROM alpine:3 AS builder
WORKDIR /build
RUN apk add --no-cache bash font-overpass git imagemagick make py3-pip python3-dev
COPY . .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt && \
    wget -q https://github.com/tdewolff/minify/releases/download/v2.9.10/minify_linux_amd64.tar.gz && \
    tar -xvf minify*.tar.gz -C /bin && \
    make

FROM alpine:3
RUN apk add --no-cache lighttpd && \
    echo 'server.error-handler-404 = "/404"' >> /etc/lighttpd/lighttpd.conf && \
    sed -i 's|/run/lighttpd.pid|/tmp/lighttpd.pid|' /etc/lighttpd/lighttpd.conf && \
    adduser -S streambinder
USER streambinder
COPY --from=builder /build /var/www/localhost/htdocs
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
HEALTHCHECK CMD [ "/usr/bin/curl", "127.0.0.1" ]
LABEL org.opencontainers.image.source=https://github.com/streambinder/streambinder

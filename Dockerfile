FROM alpine as builder
RUN apk add --no-cache bash font-overpass git imagemagick make py3-pip python3-dev
RUN pip install --break-system-packages --upgrade pip
COPY . .
RUN pip install --break-system-packages -r requirements.txt
RUN wget https://github.com/tdewolff/minify/releases/download/v2.9.10/minify_linux_amd64.tar.gz
RUN tar -xvf minify*.tar.gz -C /bin
RUN make

FROM alpine
RUN apk add --no-cache lighttpd
RUN echo 'server.error-handler-404 = "/404"' >> /etc/lighttpd/lighttpd.conf
COPY --from=builder /build /var/www/localhost/htdocs
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
LABEL org.opencontainers.image.source https://github.com/streambinder/streambinder

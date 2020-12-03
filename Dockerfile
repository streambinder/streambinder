FROM alpine as builder
RUN apk add --no-cache bash font-noto git imagemagick make py3-pip
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install markdown jinja2 pygments pyyaml requests
RUN wget https://github.com/tdewolff/minify/releases/download/v2.9.10/minify_linux_amd64.tar.gz
RUN tar -xvf minify*.tar.gz -C /bin
COPY . .
RUN make

FROM alpine
RUN apk add --no-cache lighttpd
COPY --from=builder /build /var/www/localhost/htdocs
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
LABEL org.opencontainers.image.source https://github.com/streambinder/streambinder


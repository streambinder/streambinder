#!/bin/bash

find public -type f | while read -r fname; do
    case "${fname##*.}" in
        html|css|js|json|svg|xml)
            minify "${fname}" -o "/tmp/${fname}" && \
                mv -f "/tmp/${fname}" "${fname}"
            ;;
        png)
            optipng -strip all -silent -o7 "${fname}" -out "/tmp/${fname}" && \
                mv -f "/tmp/${fname}" "${fname}"
            ;;
        jpg|jpeg) \
            jpegoptim -osqf "${fname}" -d /tmp && \
                mv -f "/tmp/${fname}" "${fname}"
            ;;
        *)
            ;;
    esac
done

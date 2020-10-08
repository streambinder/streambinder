#!/bin/bash

if [ -z "${PUB_KEY}" ]; then
    echo Missing credentials
    exit 1
fi

echo "${PUB_KEY}" > "${HOME}/id_streambinder"
rsync -av --delete -e "ssh -i ${HOME}/id_streambinder" "${BUILD_DIR}"/ dpuccissh@vps.davidepucci.it:/web/
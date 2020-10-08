#!/bin/bash

if [ -z "${PUB_KEY}" ]; then
    echo Missing credentials
    exit 1
fi

echo "${PUB_KEY}" > "${HOME}/key"
chmod 600 "${HOME}/key"
rsync -av --delete -e "ssh -i ${HOME}/key -o StrictHostKeyChecking=no" "${BUILD_DIR}"/ dpuccissh@vps.davidepucci.it:/web/
#!/bin/bash

echo "${GITHUB_ACTIONS_DAVIDEPUCCI}" | docker login ghcr.io -u streambinder --password-stdin
docker build -t ghcr.io/streambinder/streambinder:latest .
docker push ghcr.io/streambinder/streambinder:latest

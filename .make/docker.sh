#!/bin/bash

docker build . -t streambinder/davidepucci:latest
docker push streambinder/davidepucci:latest

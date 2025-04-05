#!/bin/bash
#
# Build a dockers images
#
BASE_PATH="/home/andriy/symai"
pushd ../../server/docker
sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp docker compose build
popd

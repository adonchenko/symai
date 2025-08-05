#!/bin/bash
#
# Script that starts the dockers
#
BASE_PATH="/home/andriy/symai"
pushd ../../server/docker
sudo LOGDIR=${BASE_PATH}/logdir PROPERTIES=${BASE_PATH}/properties TMPDIR=${BASE_PATH}/temp RESOURCES=${BASE_PATH}/resources docker compose up
popd



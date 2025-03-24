#!/bin/bash
#
# Build a docker image
#
pushd ../../server
sudo docker build -t symai-expression:0.0.1 . -f docker/Dockerfile
popd

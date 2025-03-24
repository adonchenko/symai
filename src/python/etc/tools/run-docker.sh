#!/bin/bash
#
# Script that starts a doker
#
LOGDIR=$HOME/symai/logdir
PROPERTIES=$HOME/symai/properties
sudo docker run -it --net host -p 8080:8080 -v $PROPERTIES:/properties -v $LOGDIR:/logdir symai-expression:0.0.1 



#!/usr/bin/env bash

#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
# SCRIPTS_DIR=$FILE_DIR
# ROOT_DIR=$(dirname $SCRIPTS_DIR)

sudo apt-get -y install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt-get -y install nginx

pip install -U -r $FILE_DIR/requirements.server.txt


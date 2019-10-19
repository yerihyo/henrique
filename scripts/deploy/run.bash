#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

SCRIPTS_DIR=$(dirname $FILE_DIR)
REPO_DIR=$(dirname $SCRIPTS_DIR)

errcho(){ >&2 echo $@; }

errcho "[$FILE_NAME] START"

pushd $REPO_DIR
$FILE_DIR/uwsgi/run.bash
$FILE_DIR/nginx/run.bash
popd

errcho "[$FILE_NAME] END"

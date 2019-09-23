#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

SCRIPTS_DIR=$(dirname $FILE_DIR)
REPO_DIR=$(dirname $SCRIPTS_DIR)

mkdir -p $FILE_DIR/tmp

jinja2 "$FILE_DIR/filelist.tmplt.list" \
    -D ENV_DIR="$REPO_DIR/env" \
    -D REPO_DIR="$REPO_DIR" \
    > $FILE_DIR/tmp/filelist.list

echo $FILE_DIR/tmp/filelist.list

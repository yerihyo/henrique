#!/bin/bash -eu
# REFERENCE: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
# FILE_PATH=$HOME/projects/lbox/henrique/scripts/deploy/uwsgi/run.bash
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)
DEPLOY_DIR=$(dirname $FILE_DIR)
SCRIPTS_DIR=$(dirname $DEPLOY_DIR)
REPO_DIR=$(dirname $SCRIPTS_DIR)

MAIN_DIR=$REPO_DIR/henrique/app/main
PROJECT_NAME=henrique

USERNAME=$(stat -c '%U' $FILE_PATH)
#GROUPNAME=$(stat -c '%G' $FILE_PATH)

errcho(){ >&2 echo $@; }

main(){
    FILEPATH_SOCK="$FILE_DIR/$PROJECT_NAME.sock"

    jinja2 $FILE_DIR/$PROJECT_NAME.tmplt.ini \
        -D FILEPATH_SOCK="$FILEPATH_SOCK" \
        -D REPO_DIR="$REPO_DIR" \
        > "$FILE_DIR/$PROJECT_NAME.ini"

    cat $SCRIPTS_DIR/docker/env.$ENV.list >> "$FILE_DIR/$PROJECT_NAME.ini"
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"


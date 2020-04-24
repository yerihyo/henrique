#!/bin/bash -eu
# REFERENCE: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)

MAIN_DIR=$REPO_DIR/henrique/app/main
PROJECT_NAME=henrique

USERNAME=$(stat -c '%U' $FILE_PATH)
#GROUPNAME=$(stat -c '%G' $FILE_PATH)

main(){
    mkdir -p $REPO_DIR/log

#    errcho "FILE_DIR: $FILE_DIR"

    jinja2 $FILE_DIR/$PROJECT_NAME.uwsgi.ini.tmplt \
        -D REPO_DIR=$REPO_DIR \
        -D mode="local" \
        > "$FILE_DIR/$PROJECT_NAME.uwsgi.local.ini"

   jinja2 $FILE_DIR/$PROJECT_NAME.uwsgi.ini.tmplt \
        -D REPO_DIR="/app" \
        -D mode="docker" \
        > "$FILE_DIR/$PROJECT_NAME.uwsgi.docker.ini"

#        -D SOCKET_HTTP="socket = /app/scripts/deploy/uwsgi/$PROJECT_NAME.uwsgi.sock" \
#        -D REPO_DIR="$REPO_DIR" \

}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"


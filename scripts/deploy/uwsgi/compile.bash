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

if [[ "$ENV" == "local" || ! "$ENV" ]]; then
    mode="local"
else
    mode="docker"
fi

main(){
    mkdir -p $REPO_DIR/log

    jinja2 $FILE_DIR/$PROJECT_NAME.uwsgi.ini.tmplt \
        -D mode="$mode" \
        > "$FILE_DIR/$PROJECT_NAME.uwsgi.$mode.ini"
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"


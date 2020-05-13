#!/bin/bash -eu
# REFERENCE: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 5)

main(){
    $FILE_DIR/compile.bash

    mkdir -p $REPO_DIR/log/uwsgi
    uwsgi "$REPO_DIR/henrique/main/singleton/deploy/uwsgi/ini/henrique.uwsgi.nginx.ini" # --uid www-data --gid www-data
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"


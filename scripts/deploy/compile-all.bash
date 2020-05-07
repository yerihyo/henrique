#!/usr/bin/env bash

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)


errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 2)
FOXYLIB_DIR=${FOXYLIB_DIR?'missing $FOXYLIB_DIR'}
export PYTHONPATH=$FOXYLIB_DIR

main(){
    pushd $REPO_DIR
    python -m henrique.main.singleton.deploy.uwsgi.henrique_uwsgi
    python -m henrique.main.singleton.deploy.nginx.henrique_nginx
    python -m henrique.main.singleton.deploy.supervisord.henrique_supervisord
    popd
}


errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"

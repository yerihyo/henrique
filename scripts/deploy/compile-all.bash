#!/usr/bin/env bash

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)


errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 2)
FOXYLIB_DIR=${FOXYLIB_DIR?''}
if [[ "$FOXYLIB_DIR" ]]; then
    export PYTHONPATH=$FOXYLIB_DIR
fi

compile_docker(){
    python -m henrique.main.singleton.env.henrique_env

    mkdir -p travis/henrique/env/docker
    for env in local dev prod; do
        travis encrypt-file \
            henrique/env/docker/env.$env.list \
            travis/henrique/env/docker/env.$env.list.enc \
            --force --com --add
    done
}

main(){
    pushd $REPO_DIR
    compile_docker
    python -m henrique.main.singleton.deploy.uwsgi.henrique_uwsgi
    python -m henrique.main.singleton.deploy.nginx.henrique_nginx
    python -m henrique.main.singleton.deploy.supervisord.henrique_supervisord
    popd
}


errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"

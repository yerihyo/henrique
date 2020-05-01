#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

ENV=${ENV?'missing $ENV'}
if [[ ! "$ENV" ]]; then errcho "missing env variable $ENV"; exit 1; fi


errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)

main(){
    pushd $REPO_DIR

    $REPO_DIR/scripts/deploy/uwsgi/compile.bash
    $REPO_DIR/scripts/deploy/nginx/compile.bash

    docker build "$@" \
        -t foxytrixy/henrique:$ENV \
        --build-arg ENV=$ENV \
        -f $FILE_DIR/Dockerfile \
        $REPO_DIR

    ##########
    # secret
    # https://docs.docker.com/engine/swarm/secrets/


    docker push foxytrixy/henrique:$ENV

    popd
}


errcho "[$FILE_NAME] START"
main "$@"
errcho "[$FILE_NAME] END"

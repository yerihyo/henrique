#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

ENV=${ENV?'missing $ENV'}
if [[ ! "$ENV" ]]; then errcho "missing env variable $ENV"; exit 1; fi


errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)
env_filepath="$REPO_DIR/henrique/env/docker/env.$ENV.list"

main(){
    pushd $REPO_DIR

    docker run \
        --env ENV=$ENV \
        --env-file $env_filepath \
        -it \
        --volume $HOME/env:/app/env:ro \
        --volume $REPO_DIR/log:/app/log \
        --publish 80:80 \
        --publish 443:443 \
        foxytrixy/henrique \
        supervisord -n -c /app/henrique/main/singleton/deploy/supervisord/conf/henrique.supervisord.$ENV.conf

    popd
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"

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
docker_image=foxytrixy/henrique:$ENV

compile(){
    $REPO_DIR/scripts/deploy/uwsgi/compile.bash
    $REPO_DIR/scripts/deploy/nginx/compile.bash

    if [[ $ENV == "local" ]]; then
        env_filepath="$REPO_DIR/henrique/env/docker/env.$ENV.list"
    else
        env_filepath="/home/ubuntu/tmp/henrique/env/docker/env.$ENV.list"
    fi

    jinja2 $FILE_DIR/docker-compose.yml.tmplt \
            -D ENV="$ENV" \
            -D env_filepath="$env_filepath" \
            > $FILE_DIR/docker-compose.$ENV.yml

#    env_filepath="$REPO_DIR/henrique/env/docker/env.$ENV.list"

    dirname $env_filepath | xargs -I {} mkdir -p "{}"
    python -m henrique.main.singleton.env.henrique_env $ENV > $env_filepath
}

main(){
    pushd $REPO_DIR

    # https://stackoverflow.com/questions/41498336/docker-copy-not-updating-files-when-rebuilding-container
#    docker build "$@" \
#        -t $docker_image \
#        --build-arg ENV=$ENV \
#        -f $FILE_DIR/Dockerfile \
#        $REPO_DIR

    compile
    docker-compose -f $FILE_DIR/docker-compose.$ENV.yml build "$@"

    ##########
    # secret
    # https://docs.docker.com/engine/swarm/secrets/


#    docker push $docker_image

    popd
}


errcho "[$FILE_NAME] START"
main "$@" # --no-cache --force-rm
errcho "[$FILE_NAME] END"

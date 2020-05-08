#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

#ENV=${ENV?'missing $ENV'}
#if [[ ! "$ENV" ]]; then errcho "missing env variable $ENV"; exit 1; fi


errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)
#docker_image=foxytrixy/henrique:$ENV
docker_image=foxytrixy/henrique

main(){
    pushd $REPO_DIR

#    $REPO_DIR/scripts/deploy/compile-all.bash  # assuming this is already done
    docker build "$@" \
        -t $docker_image \
        -f $FILE_DIR/Dockerfile \
        $REPO_DIR

#    --build-arg ENV=$ENV \

    ##########
    # secret
    # https://docs.docker.com/engine/swarm/secrets/


    docker push $docker_image

    popd
}


errcho "[$FILE_NAME] START"
main "$@" # --no-cache --force-rm
errcho "[$FILE_NAME] END"

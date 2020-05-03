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
env_filepath="$REPO_DIR/henrique/env/docker/env.$ENV.list"

main(){
    pushd $REPO_DIR

    mkdir -p $REPO_DIR/henrique/env/docker/
    python -m henrique.main.singleton.env.henrique_env $ENV > $env_filepath
    docker run \
        --env-file $env_filepath \
        -it \
        -v $REPO_DIR/log:/app/log \
        -p 80:80 \
        -p 443:443 \
        foxytrixy/henrique:$ENV

#        -d \

    popd
}


#remove_all_containers(){
#    # Remove all containers
#    sudo docker stop $(sudo docker ps -a -q)
#    sudo docker rm $(sudo docker ps -a -q)
#}
#
#remove_all_images(){
#    # Remove all images
#    sudo docker rmi $(sudo docker images -q)
#}

errcho "[$FILE_NAME] START"
#$FILE_DIR/build.bash
main
errcho "[$FILE_NAME] END"

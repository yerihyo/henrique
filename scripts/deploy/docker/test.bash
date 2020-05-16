#!/bin/bash -eux

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)


#ENV=${ENV?'missing $ENV'}
#if [[ ! "$ENV" ]]; then errcho "missing env variable $ENV"; exit 1; fi


errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)

TRAVIS_BRANCH=${TRAVIS_BRANCH?'missing $TRAVIS_BRANCH'}

#TAG=${TAG?'missing $TAG'}
branch2env(){
    local branch=${1?'missing $1'}
    if [[ "$branch" == "master" ]]; then
        errcho "branch2env: P"
        echo "prod"
    else
        errcho "branch2env: D"
        echo "dev"
    fi
}

main(){
    pushd $REPO_DIR

    local uuid=$(python -c "import uuid; print(uuid.uuid4().hex);")
    #local tag_test="unittest-${ENV}-${uuid}"
    local env=$(branch2env "$TRAVIS_BRANCH")
    local tag="$env"
    local docker_image=foxytrixy/henrique
    local env_filepath="$REPO_DIR/henrique/env/docker/env.${ENV}.list"

    errcho "[$FILE_NAME] main - TRAVIS_BRANCH=$TRAVIS_BRANCH env=$env, tag=$tag"

    docker build \
        -t ${docker_image}:${tag} \
        -f $FILE_DIR/Dockerfile \
        $REPO_DIR
#    --build-arg ENV=$ENV \

    ##########
    # secret
    # https://docs.docker.com/engine/swarm/secrets/

    docker login

    docker run \
        --env ENV=$ENV \
        --env-file $env_filepath \
        -it \
        --volume $REPO_DIR/henrique/env:/app/env:ro \
        --volume $REPO_DIR/log:/app/log \
        ${docker_image}:${tag} \
        pytest

    docker push ${docker_image}:${tag}

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
main "$@"
errcho "[$FILE_NAME] END"

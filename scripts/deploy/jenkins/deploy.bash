#!/usr/bin/env bash -euf

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

errcho(){ >&2 echo "$@"; }

ENV=${ENV?'missing $ENV'}

PROJECTS_DIR=$HOME/projects
export FOXYLIB_DIR=$PROJECTS_DIR/foxylib
HENRIQUE_DIR=$PROJECTS_DIR/henrique

# DOCKER_PASSWORD=${DOCKER_PASSWORD?'missing $DOCKER_PASSWORD'}

pull_foxylib(){
    pushd $FOXYLIB_DIR
    git pull origin master
    . venv/bin/activate
    python setup.py install
    deactivate
    popd
}

pull_henrique(){
    pushd $HENRIQUE_DIR
    . venv/bin/activate
    pip3 install -U -r henrique/requirements.txt

    ./scripts/lpass/pull.bash
    . ./scripts/direnv/load.bash

    # echo $DOCKER_PASSWORD | docker login --username $DOCKER_USERNAME

    ENV=$ENV ./scripts/deploy/remote/deploy.bash stop
    ENV=$ENV ./scripts/deploy/remote/deploy.bash start
    deactivate
    popd

}

main(){
    pull_foxylib || exit 1
    pull_henrique || exit 1
}

main || exit 1

# jenkins active exited
# https://stackoverflow.com/questions/42607771/jenkins-active-exited

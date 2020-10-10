#!/usr/bin/env bash
set -eux

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

errcho(){ >&2 echo "$@"; }

ENV=${ENV?'missing $ENV'}

PROJECTS_DIR=$HOME/projects
export FOXYLIB_DIR=$PROJECTS_DIR/foxylib
HENRIQUE_DIR=$PROJECTS_DIR/henrique

PYTHON=python3.8

# DOCKER_PASSWORD=${DOCKER_PASSWORD?'missing $DOCKER_PASSWORD'}

pull_foxylib(){
    pushd $FOXYLIB_DIR
    git pull origin master

    set +eu
    . venv/bin/activate
    set -eu

    rm -Rf build
    $PYTHON setup.py install
    deactivate
    popd
}

pull_henrique(){
    pushd $HENRIQUE_DIR
    set +eu
    . venv/bin/activate
    set -eu

    pip3 install -U -r henrique/requirements.txt

    ./scripts/lpass/pull.bash || exit 1
    . ./scripts/direnv/load.bash || exit 1

    # echo $DOCKER_PASSWORD | docker login --username $DOCKER_USERNAME

    # TAG=$ENV ./scripts/deploy/docker/build.bash
    python=$PYTHON ENV=$ENV ./scripts/deploy/remote/deploy.bash stop
    python=$PYTHON ENV=$ENV ./scripts/deploy/remote/deploy.bash start
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

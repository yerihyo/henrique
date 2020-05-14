#!/usr/bin/env bash -eu

# https://medium.com/@ekwinder/setting-up-uwsgi-with-nginx-on-macos-for-python-web-apps-25edf4edab19

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 4)
DEPLOY_DIR=$(func_count2reduce $FILE_DIR dirname 2)

PYTHON_VERSION="3.6.9"
USER=${USER?'missing $USER'}
ENV=local

run_nginx(){
    brew install nginx

    ENV=$ENV $DEPLOY_DIR/nginx/build_conf.bash
    if [[ ! -e /usr/local/etc/nginx/nginx.conf.ori ]]; then
        mv /usr/local/etc/nginx/nginx.conf /usr/local/etc/nginx/nginx.conf.ori
    fi

    mv $DEPLOY_DIR/nginx/nginx.conf /usr/local/etc/nginx/nginx.conf
}

main(){
    brew update
    brew install pyenv
    pyenv install $PYTHON_VERSION


    PYTHON=/Users/$USER/.pyenv/versions/$PYTHON_VERSION/bin/python3
    PIP=pip3

    PYTHON=$PYTHON PIP=$PIP $DEPLOY_DIR/pip.install.bash

    run_nginx


}

main
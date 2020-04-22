#!/usr/bin/env bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

DEPLOY_DIR=$FILE_DIR

main(){
    sudo apt-get -y install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
    sudo apt-get -y install nginx

    pip install -U -r $DEPLOY_DIR/requirements.server.txt
}

main
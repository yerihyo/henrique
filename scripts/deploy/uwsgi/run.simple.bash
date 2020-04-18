#!/bin/bash -eu
# REFERENCE: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

export REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)

VENV_DIR=$REPO_DIR/venv
. $VENV_DIR/bin/activate
pip3 install -r $FILE_DIR/../requirements.server.txt

MAIN_DIR=$REPO_DIR/henrique/app/main
PROJECT_NAME=henrique

#USERNAME=$(stat -c '%U' $FILE_PATH)
#GROUPNAME=$(stat -c '%G' $FILE_PATH)

main(){
    $VENV_DIR/bin/uwsgi \
        --socket 0.0.0.0:14920 \
        --protocol=http \
        --wsgi henrique.main.run:app
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"


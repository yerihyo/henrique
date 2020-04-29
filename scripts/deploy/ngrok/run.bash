#!/usr/bin/env bash


FILE_PATH=$(readlink -f $0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)
# FILE_DIR=`pwd`/../scripts/test
SCRIPTS_DIR=$FILE_DIR

errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)
NGROK=$HOME/scripts/ngrok/ngrok


main(){
    # $NGROK authtoken --config $FILE_DIR/ngrok.yml $NGROK_AUTHTOKEN
    $NGROK http -config=$FILE_DIR/ngrok.yml 14920
}

main
#!/bin/bash -eu

ARG0=$BASH_SOURCE[0]
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)

FILE_NAME=$(basename $FILE_PATH)

errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce "$FILE_DIR" dirname 3)
FOXYLIB_DIR=${FOXYLIB_DIR?'missing $FOXYLIB_DIR'}

export PYTHONPATH=$FOXYLIB_DIR
export SKIP_WARMUP=1

main(){
    pushd $REPO_DIR
    #python -m scripts.mongodb.postgres2mongodb.port2mongodb
    #python -m scripts.mongodb.postgres2mongodb.tradegood2mongodb
    python -m scripts.mongodb.postgres2mongodb.porttradegoodstate2markettrend
    popd
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"

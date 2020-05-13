#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 2)
FOXYLIB_DIR=${FOXYLIB_DIR?'missing $FOXYLIB_DIR'}

export SKIP_WARMUP="" #1
export FLASK_ENV=development
export PYTHONPATH=$FOXYLIB_DIR:$REPO_DIR

main(){
    pushd $REPO_DIR
    #pip install -U -r henrique/requirements.txt
    pytest "$@"
    popd
}

errcho "[$FILE_NAME] START"
main "$@"
errcho "[$FILE_NAME] END"

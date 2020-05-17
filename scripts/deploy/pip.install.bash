#!/usr/bin/env bash
set -eux

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 2)
DEPLOY_DIR=$FILE_DIR

PYTHON=${PYTHON?'missing $PYTHON'}
PIP=${PIP?'missing $PIP'}

main(){
    pushd $REPO_DIR

    if [[ ! -e $REPO_DIR/venv ]]; then
        $PYTHON -m venv $REPO_DIR/venv
    fi

    . $REPO_DIR/venv/bin/activate

    $PIP install -U pip
    $PIP install -U setuptools==41.0.1
    $PIP install -U -r $REPO_DIR/henrique/requirements.txt
    $PIP install -U -r $DEPLOY_DIR/requirements.server.txt

    popd
}

main

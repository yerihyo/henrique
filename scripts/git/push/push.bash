#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)
branch="${1:-$(git branch | grep '\*' | awk '{print $2}')}"

main(){
    pushd $REPO_DIR

    $FILE_DIR/compile-all.bash
    git push origin "$branch"

    popd
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"



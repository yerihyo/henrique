#!/bin/bash 

set -e
set -u


ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 2)

branch="$(git branch | grep '\*' | awk '{print $2}')"
target=develop

main(){
    pushd $REPO_DIR

    git push origin $branch
    git checkout $target
    git merge --no-ff $branch
    $FILE_DIR/push/push.bash "$branch"
    git checkout $branch

    popd
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"


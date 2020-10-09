#!/bin/bash -f

set -e
set -u

FILE_PATH=$(readlink -f $0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 1)


#export LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"

main(){
    pushd $REPO_DIR
#    xcode-select --install

    pip install -U -r henrique/requirements.txt
    popd
}

errcho "[$FILE_NAME] START"
main "$@"
errcho "[$FILE_NAME] END"
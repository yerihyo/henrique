#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

SCRIPTS_DIR=$(dirname $FILE_DIR)
REPO_DIR=$(dirname $SCRIPTS_DIR)

errcho(){ >&2 echo "$@"; }
usage(){ errcho "usage: $ARG0 <env>"; }

env="${1:-}"
if [[ ! "$env" ]]; then usage; exit 1; fi 

main(){
    pushd $REPO_DIR

    # Create env.$env.list
    cat $REPO_DIR/.envrc \
        | sed 's/^export //g;s/"//g;' \
        > "$FILE_DIR/env.$env.list"

    errcho "[ENV] env.$env.list"
#    >&2 cat "$FILE_DIR/env.$env.list"

    # Create Docker Image
    sudo docker build -t foxytrixy/henrique:$env \
                        --build-arg ENV=$env \
                        -f $FILE_DIR/Dockerfile .

    # Push Docker Image to Docker hub
    sudo docker push foxytrixy/henrique:$env
    popd
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"

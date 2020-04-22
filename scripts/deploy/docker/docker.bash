#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

SCRIPTS_DIR=$(dirname $FILE_DIR)
REPO_DIR=$(dirname $SCRIPTS_DIR)

errcho(){ >&2 echo $@; }
usage(){ errcho "usage: $ARG0 <env>"; }

env="${1:-}"
if [[ ! "$env" ]]; then usage; exit 1; fi 


main(){
    pushd $REPO_DIR

    # Create env.$env.list
    cat $REPO_DIR/.envrc \
            | sed 's/^export //g;s/"//g;' \
              >> "$FILE_DIR/env.$env.list"

    sudo docker build -t henrique:$env --build-arg ENV=$env -f $FILE_DIR/Dockerfile .
    sudo docker run --env-file $FILE_DIR/env.$env.list -it --privileged -v $REPO_DIR/log:/henrique/log -d -p 80:80 -p 443:443 henrique:$env

    popd
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"

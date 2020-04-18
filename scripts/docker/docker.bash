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

errcho "[$FILE_NAME] DOCKER BUILD and DEPLOYMENT START"

pushd $REPO_DIR

# Create env.$env.list
cat $REPO_DIR/.envrc \
        | sed 's/^export //g;s/"//g;' \
          >> "$FILE_DIR/env.$env.list"

# Create Docker Image
sudo docker build -t delphi:$env --build-arg ENV=$env -f $FILE_DIR/Dockerfile .

# Run Docker container with image
sudo docker run --env-file $FILE_DIR/env.$env.list -it --privileged -v $REPO_DIR/log:/delphi/log -d -p 80:80 -p 443:443 delphi:$env
popd

errcho "[$FILE_NAME] DOCKER BUILD and DEPLOYMENT END"

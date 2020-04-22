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

case "$env" in
  prod|production) server_name=henrique-lightsail-prod;;
  dev|development) server_name=henrique-lightsail-dev
esac

main(){
    pushd $REPO_DIR

    ip=$($SCRIPTS_DIR/server/server_name2ip.bash "$server_name")
    errcho "server_name=$server_name ip=$ip"

    # Transfer env list into server
    scp $FILE_DIR/env.$env.list ubuntu@$ip:/home/ubuntu/

    # Remotely Execute Docker Container
    ssh ubuntu@$ip 'bash -s' < $FILE_DIR/deploy.bash $env

    popd
}

errcho "[$FILE_NAME] START ($server_name)"
main
errcho "[$FILE_NAME] END ($server_name)"

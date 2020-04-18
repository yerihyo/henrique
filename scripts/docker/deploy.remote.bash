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
  prod|production) server_name=delphi-lightsail-prod;;
  dev|development) server_name=delphi-lightsail-dev
esac

main(){
    ip=$($SCRIPTS_DIR/server/server_name2ip.bash "$server_name")
    errcho "server_name=$server_name ip=$ip"

    # Transfer env list into server
    scp $FILE_DIR/env.$env.list ubuntu@$ip:/home/ubuntu/

    # Remotely Execute Docker Container
    ssh ubuntu@$ip 'bash -s' < $FILE_DIR/deploy.bash $env
}

errcho "[$FILE_NAME] START ($server_name)"
pushd $REPO_DIR
main
popd
errcho "[$FILE_NAME] END ($server_name)"

#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo $@; }
usage(){ errcho "usage: $ARG0 <env>"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)

ENV=${ENV?'missing ENV'}
USERNAME="ubuntu"

IP=$(python -m scripts.deploy.remote.henrique_server $ENV)
if [[ ! "$IP" ]]; then errcho "no 'IP'"; exit 1; fi

env_filepath="$REPO_DIR/henrique/env/docker/env.$ENV.list"
mkdir -p $REPO_DIR/henrique/env/docker

pem_filepath=$REPO_DIR/henrique/env/aws/lightsail/key_pair/$ENV.henrique.pem
SSH="ssh -i $pem_filepath $USERNAME@$IP"
SCP="scp -i $pem_filepath"

main(){
    errcho "[$FILE_NAME] main() - START"
    pushd $REPO_DIR

    python -m henrique.main.singleton.env.henrique_env $ENV > "$env_filepath"
    ENV=$ENV $REPO_DIR/scripts/deploy/docker/build.bash
    #ENV=$ENV $REPO_DIR/scripts/deploy/docker/push.bash

    # Transfer env list into server
    echo "mkdir -p /home/$USERNAME/env" | $SSH 'bash -s'
    $SCP $env_filepath $USERNAME@$IP:/home/$USERNAME/env/

    # Remotely Execute Docker Container
    $SSH 'bash -s' < $FILE_DIR/run.bash $ENV

    popd
    errcho "[$FILE_NAME] main() - END"
}

errcho "[$FILE_NAME] START (ENV:$ENV, IP:$IP)"
main
errcho "[$FILE_NAME] END (ENV:$ENV, IP:$IP)"

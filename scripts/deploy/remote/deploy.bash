#!/bin/bash -eu

if [[ -f $HOME/.bashrc ]]; then source $HOME/.bashrc; fi

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo $@; }
usage(){ errcho "usage: $ARG0 <filepath_script>"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

filepath_script="${1:-}"
if [[ ! "$filepath_script" ]]; then usage; exit 1; fi

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)

ENV=${ENV?'missing ENV'}
USERNAME="ubuntu"

IP=$(python -m scripts.deploy.remote.henrique_server $ENV)
if [[ ! "$IP" ]]; then errcho "no 'IP'"; exit 1; fi

AUTHORITY="$USERNAME@$IP"

env_filepath="$REPO_DIR/henrique/env/docker/env.$ENV.list"
mkdir -p $REPO_DIR/henrique/env/docker

pem_filepath=$REPO_DIR/henrique/env/aws/lightsail/key_pair/$ENV.henrique.pem
SSH="ssh -i $pem_filepath $USERNAME@$IP"
SCP="scp -i $pem_filepath"
#RSYNC="rsync --delete -azv -e 'ssh -i $pem_filepath'"
RSYNCOPT=(--delete -azv -e "ssh -i $pem_filepath")

rsync_env(){
    # Transfer env list into server
    errcho "[$FILE_NAME] rsync_env() - START"

    echo "mkdir -p /home/$USERNAME/env" | $SSH 'bash -s'
    rsync "${RSYNCOPT[@]}" -r $REPO_DIR/henrique/env/ $AUTHORITY:/home/$USERNAME/env/
    rsync "${RSYNCOPT[@]}" $env_filepath $AUTHORITY:/home/$USERNAME/env/env.$ENV.list
#    $SCP $env_filepath $AUTHORITY:/home/$USERNAME/env/

    errcho "[$FILE_NAME] rsync_env() - END"
}

main(){
    errcho "[$FILE_NAME] main() - START"
    pushd $REPO_DIR

    ENV=$ENV $REPO_DIR/scripts/deploy/docker/build.bash
    #ENV=$ENV $REPO_DIR/scripts/deploy/docker/push.bash

    rsync_env

    # Remotely Execute Docker Container
    $SSH 'bash -s' < $filepath_script $ENV

    popd
    errcho "[$FILE_NAME] main() - END"
}



errcho "[$FILE_NAME] START (ENV:$ENV, IP:$IP, filepath_script:$filepath_script)"
main
errcho "[$FILE_NAME] END (ENV:$ENV, IP:$IP, filepath_script:$filepath_script)"

#!/bin/bash -eux

if [[ -f $HOME/.bashrc ]]; then . $HOME/.bashrc; fi

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo "$@"; }
usage(){ errcho "usage: $ARG0 <option>"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

option="${1:-}"
if [[ ! "$option" ]]; then usage; exit 1; fi


lightsail(){
REPO_DIR="/var/lib/jenkins/projects/henrique"
ENV="prod"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)
ENV=${ENV?'missing ENV'}
USERNAME="ubuntu"

IP=$(ENV=$ENV python -m scripts.deploy.remote.henrique_server)
if [[ ! "$IP" ]]; then errcho "no 'IP'"; exit 1; fi

AUTHORITY="$USERNAME@$IP"

env_filepath="$REPO_DIR/henrique/env/docker/env.$ENV.list"
mkdir -p $REPO_DIR/henrique/env/docker

pem_filepath=$REPO_DIR/henrique/env/aws/lightsail/key_pair/$ENV.henrique.pem
chmod 400 $pem_filepath
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

option2filepath_script(){
    if [[ "$option" == "start" ]]; then
        echo "$REPO_DIR/scripts/deploy/remote/server/start.bash"
    elif [[ "$option" == "stop" ]]; then
        echo "$REPO_DIR/scripts/deploy/remote/server/stop.bash"
    else
        errcho "invalid option: $option"
        exit 1
    fi
}

main(){
    errcho "[$FILE_NAME] main() - START"
    pushd $REPO_DIR

    python -m henrique.main.singleton.env.henrique_env

#    if [[ "$option" == "start" ]]; then
#        TAG=${ENV} $REPO_DIR/scripts/deploy/docker/build.bash
#    fi
    #ENV=$ENV $REPO_DIR/scripts/deploy/docker/push.bash

    rsync_env || exit 1

    filepath_script=$(option2filepath_script) || exit 1
    errcho "[$FILE_NAME] main - filepath_script:$filepath_script"
    # Remotely Execute Docker Container
    $SSH 'bash -s' < $filepath_script $ENV

    popd
    errcho "[$FILE_NAME] main() - END"
}



errcho "[$FILE_NAME] START (ENV:$ENV, IP:$IP)"
main || exit 1
errcho "[$FILE_NAME] END (ENV:$ENV, IP:$IP)"

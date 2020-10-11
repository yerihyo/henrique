#!/bin/bash -eux

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo "$@"; }
usage(){ errcho "usage: $ARG0"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}


REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)
ENV=${ENV?'missing ENV'}
USERNAME="ubuntu"

IP=$(python -m scripts.deploy.remote.server "jenkins.ip")
if [[ ! "$IP" ]]; then errcho "no 'IP'"; exit 1; fi

AUTHORITY="$USERNAME@$IP"

pem_filepath=$REPO_DIR/henrique/env/aws/lightsail/key_pair/$ENV.henrique.pem
chmod 400 $pem_filepath
SSH="ssh -i $pem_filepath -o StrictHostKeyChecking=no $USERNAME@$IP"

main(){
    errcho "[$FILE_NAME] main() - START"
    pushd $REPO_DIR

    $SSH

    popd
    errcho "[$FILE_NAME] main() - END"
}



errcho "[$FILE_NAME] START (ENV:$ENV, IP:$IP)"
main || exit 1
errcho "[$FILE_NAME] END (ENV:$ENV, IP:$IP)"

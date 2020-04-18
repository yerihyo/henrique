#!/bin/bash -eu

errcho(){ >&2 echo $@; }
usage(){ errcho "usage: $ARG0 <env>"; }

env="${1:-}"

if [[ ! "$env" ]]; then usage; exit 1; fi


clear_containers(){
    set +e

    # Stop running containers
    sudo docker stop $(sudo docker ps -a -q)
    if ! [ $? -eq 0 ]; then
        errcho "Running Docker containers stopped"
    fi

    # Remove existing containers
    sudo docker rm $(sudo docker ps -a -q)
    if ! [ $? -eq 0 ]; then
        errcho "Docker containers removed"
    fi

    set -e
}

main(){
    # Pull Docker image from Docker hub
    sudo docker pull foxytrixy/henrique:$env
    errcho "Docker images pulled from Docker hub"

    # Clear existing delphi docker container
    clear_containers

    # Run Docker container with image
    sudo docker run -it --rm --privileged \
                    --env-file $HOME/env.$env.list \
                    -v $HOME/log:/delphi/log \
                    -d -p 80:80 -p 443:443 \
                    foxytrixy/henrique:$env

    errcho "delphi:$env successfully deployed!"
}



errcho "[delphi:$env] Deployment start"
main
errcho "[delphi:$env] Deployment end"

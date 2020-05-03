#!/bin/bash -eu


errcho(){ >&2 echo $@; }
FILE_NAME="stop.bash"

main(){
    errcho "[$FILE_NAME] main() - Start"

    set +e

    # Stop running containers
    local containers=$(sudo docker ps -a -q)
    if [[ "$containers" ]]; then
        sudo docker stop ${containers}
        if ! [ $? -eq 0 ]; then
            errcho "Docker containers stopped"
        fi

        # Remove existing containers
        sudo docker rm ${containers}
        if ! [ $? -eq 0 ]; then
            errcho "Docker containers removed"
        fi
    fi

    set -e
    errcho "[$FILE_NAME] main() - END"
}


errcho "[$FILE_NAME] Start"
main
errcho "[$FILE_NAME] End"

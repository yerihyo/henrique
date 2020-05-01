#!/bin/bash -eu


errcho(){ >&2 echo $@; }
FILE_NAME="run.bash"
ENV="${1:-}"
if [[ ! "$ENV" ]]; then errcho "\$ENV missing"; exit 1; fi


install(){
    errcho "[$FILE_NAME] install() - Start (ENV:$ENV)"

    # https://docs.docker.com/engine/install/ubuntu/
    sudo apt-get -y update
    sudo apt-get -y install \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-key fingerprint 0EBFCD88
    sudo add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
       $(lsb_release -cs) \
       stable"

    sudo apt-get -y update
    sudo apt-get -y install docker-ce docker-ce-cli containerd.io

    errcho "[$FILE_NAME] install() - END (ENV:$ENV)"
}

clear_containers(){
    errcho "[$FILE_NAME] clear_containers() - Start (ENV:$ENV)"

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
    errcho "[$FILE_NAME] clear_containers() - END (ENV:$ENV)"
}

main(){
    errcho "[$FILE_NAME] main() - START (ENV:$ENV)"

    # Pull Docker image from Docker hub
    errcho "[$FILE_NAME] main() - docker pull (ENV:$ENV)"
    sudo docker pull foxytrixy/henrique:$ENV
    errcho "Docker images pulled from Docker hub"

    # Clear existing docker container
    errcho "[$FILE_NAME] main() - clear_containers (ENV:$ENV)"
    clear_containers

    # Run Docker container with image
    errcho "[$FILE_NAME] main() - docker run (ENV:$ENV)"
    sudo docker run \
        --env-file $HOME/env/env.$ENV.list \
        -v $HOME/log:/app/log \
        -p 80:80 \
        -p 443:443 \
        foxytrixy/henrique

#    sudo docker run -it --rm --privileged \
#                    --env-file $HOME/env.$ENV.list \
#                    -v $HOME/log:/henrique/log \
#                    -d -p 80:80 -p 443:443 \
#                    foxytrixy/henrique:$ENV

    errcho "[$FILE_NAME] main() - END (ENV:$ENV)"
}



errcho "[$FILE_NAME] Start (ENV:$ENV)"
install
main
errcho "[$FILE_NAME] End (ENV:$ENV)"

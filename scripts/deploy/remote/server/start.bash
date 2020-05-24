#!/bin/bash -eu


errcho(){ >&2 echo "$@"; }
FILE_NAME="start.bash"
ENV="${1:-}"
if [[ ! "$ENV" ]]; then errcho "\$ENV missing"; exit 1; fi

docker_image=foxytrixy/henrique
tag="$ENV"

install(){
    errcho "[$FILE_NAME] install() - Start (ENV:$ENV)"

    # https://docs.docker.com/engine/install/ubuntu/
    sudo apt-get -y update
    DEBIAN_FRONTEND=noninteractive sudo apt-get -y install \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-key fingerprint 0EBFCD88
    sudo add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

    sudo apt-get -y update
    sudo apt-get -y install docker-ce docker-ce-cli containerd.io

    errcho "[$FILE_NAME] install() - END (ENV:$ENV)"
}

main(){
    errcho "[$FILE_NAME] main() - START (ENV:$ENV)"

    # Pull Docker image from Docker hub
    errcho "[$FILE_NAME] main() - docker pull (ENV:$ENV)"
    sudo docker pull $docker_image:$tag
    errcho "Docker images pulled from Docker hub"

    # Stop & Clean existing docker container
    #$FILE_DIR/stop.bash

    # Run Docker container with image
    errcho "[$FILE_NAME] main() - docker run (ENV:$ENV, docker_image:$docker_image)"
    sudo docker run \
        --env ENV=$ENV \
        --env-file $HOME/env/env.$ENV.list \
        --volume $HOME/log:/app/log \
        --volume $HOME/env:/app/env:ro \
        --detach \
        --publish 80:80 \
        --publish 443:443 \
        $docker_image:$tag \
        supervisord -n -c /app/henrique/main/singleton/deploy/supervisord/conf/henrique.supervisord.$ENV.conf

    errcho "[$FILE_NAME] main() - END (ENV:$ENV)"
}

tail_log(){
    sudo docker logs -f "$(sudo docker ps -a -q)"
}

errcho "[$FILE_NAME] Start (ENV:$ENV)"
install
main
errcho "[$FILE_NAME] End (ENV:$ENV)"

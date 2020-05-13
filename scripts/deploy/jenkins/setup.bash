#!/usr/bin/env bash

## java
sudo apt update
sudo apt install openjdk-8-jdk



create_key(){
    # git clone
    ssh-keygen -t rsa
    cat $HOME/.ssh/id_rsa.pub
    ## add key to github
}

install(){
    # virtualenv
    sudo apt update
    sudo apt -y install virtualenv python3-pip
    sudo apt install lastpass-cli

    # docker
    sudo apt-get remove docker docker-engine docker.io containerd runc
    sudo apt-get update
    sudo apt-get -y install \
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

    # jenkins
    # https://www.digitalocean.com/community/tutorials/how-to-install-jenkins-on-ubuntu-18-04
    ## https://stackoverflow.com/questions/49937743/install-jenkins-in-ubuntu-18-04-lts-failed-failed-to-start-lsb-start-jenkins-a  # not working

    sudo apt update
    sudo apt -y install openjdk-8-jdk

    wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -
    sudo sh -c 'echo deb http://pkg.jenkins-ci.org/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
    sudo apt update
    sudo apt -y install jenkins

    USERNAME_JENKINS="jenkins"
    sudo groupadd docker || errcho "[WARNING] groupadd: group 'docker' already exists"
    sudo usermod -aG docker "$USERNAME_JENKINS"
    sudo password "$USERNAME_JENKINS"
}


port_forwarding(){
    # port forwarding
    ## https://wiki.jenkins.io/display/JENKINS/Running+Jenkins+on+Port+80+or+443+using+iptables
    ## (script below only. do NOT adde ACCEPT lines)
    sudo iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
    sudo iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8443
}



git_clone(){
    su - jenkins

    export FOXYLIB_DIR=$HOME/jenkins/foxylib
    HENRIQUE_DIR=$HOME/jenkins/henrique
    PIP=pip3

    mkdir -p "$(dirname $HENRIQUE_DIR)"
    git clone https://github.com/yerihyo/foxylib.git $FOXYLIB_DIR

    # virtualenv
    git clone https://github.com/yerihyo/henrique.git $HENRIQUE_DIR

    pushd $HENRIQUE_DIR || exit 1
    virtualenv -p "$(which python3.6)" venv
    . $HENRIQUE_DIR/venv/bin/activate
    $PIP install -U setuptools==41.0.1
    $PIP install -U -r henrique/requirements.txt
    popd

    mkdir -p $HOME/.config/lpass $HOME/.local/share/lpass
}

run_docker(){
    export FOXYLIB_DIR=$HOME/jenkins/foxylib
    . $HENRIQUE_DIR/venv/bin/activate

    $HENRIQUE_DIR/scripts/lpass/pull.bash
    . $HENRIQUE_DIR/scripts/direnv/load.bash

    echo $DOCKER_PASSWORD | docker login --username $DOCKER_USERNAME

    pushd $HOME/jenkins/henrique
    ./scripts/deploy/remote/deploy.bash ./scripts/deploy/remote/server/start.bash
    popd
#    sudo apt-get --no-install-recommends -yqq install \
#      bash-completion \
#      build-essential \
#      cmake \
#      libcurl4  \
#      libcurl4-openssl-dev  \
#      libssl-dev  \
#      libxml2 \
#      libxml2-dev  \
#      libssl1.1 \
#      pkg-config \
#      ca-certificates \
#      xclip

}

main(){
    create_key  # need to copy key into github manually
    install
    port_forwarding
    git_clone

    run_docker
}

main

# jenkins active exited
# https://stackoverflow.com/questions/42607771/jenkins-active-exited

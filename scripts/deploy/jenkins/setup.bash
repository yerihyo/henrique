#!/usr/bin/env bash

ARG0=${BASH_SOURCE[0]}
#FILE_PATH=$(readlink -f $ARG0)
#FILE_DIR=$(dirname $FILE_PATH)
#FILE_NAME=$(basename $FILE_PATH)

errcho(){ >&2 echo "$@"; }
#usage(){ errcho "usage: $ARG0 <passphrase> <jenkins_password>"; }

#if [[ $# -lt 2 ]]; then usage; exit 1; fi

create_key(){
    passphrase=${1?'missing $1'}

    # git clone
    if [[ ! -e "$HOME/.ssh/id_rsa" ]]; then
        # ssh-keygen
        ssh-keygen -f $HOME/.ssh/id_rsa -t rsa -N "$passphrase"
    fi
    cat $HOME/.ssh/id_rsa.pub
    ## add key to github
}

git_clone(){
    sudo su - jenkins

    PROJECTS_DIR=$HOME/projects
    HENRIQUE_DIR=$PROJECTS_DIR/henrique
    PIP=pip3

    mkdir -p "$PROJECTS_DIR"
    git clone https://github.com/yerihyo/foxylib.git $PROJECTS_DIR/foxylib

    # virtualenv
    git clone https://github.com/yerihyo/henrique.git $HENRIQUE_DIR

    pushd $HENRIQUE_DIR || exit 1
    virtualenv -p "$(which python3.6)" venv
    . $HENRIQUE_DIR/venv/bin/activate
    $PIP install -U setuptools==41.0.1
    $PIP install -U -r henrique/requirements.txt
    popd

    mkdir -p $HOME/.config/lpass $HOME/.local/share/lpass
    sudo su - ubuntu
}

aptitude_install(){
    jenkins_password=${1?'missing $1'}

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

    sudo groupadd docker || errcho "[WARNING] groupadd: group 'docker' already exists"
    sudo usermod -aG docker --password "$jenkins_password" "jenkins"
}


port_forwarding(){
    # port forwarding
    ## https://wiki.jenkins.io/display/JENKINS/Running+Jenkins+on+Port+80+or+443+using+iptables
    ## (script below only. do NOT adde ACCEPT lines)
    sudo iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
    sudo iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8443
}


main(){
    create_key  # need to copy key into github manually
    git_clone

    aptitude_install
    port_forwarding
}

main

# jenkins active exited
# https://stackoverflow.com/questions/42607771/jenkins-active-exited

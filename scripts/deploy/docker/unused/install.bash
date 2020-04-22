#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}                                                          
FILE_PATH=$(readlink -f $ARG0)                                                  
FILE_DIR=$(dirname $FILE_PATH)                                                  
SCRIPTS_DIR=$FILE_DIR                                                           
REPO_DIR=$(dirname $SCRIPTS_DIR)

sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update

sudo apt install docker-ce

#!/bin/bash -eu

# Remove all containers
sudo docker stop $(sudo docker ps -a -q)
sudo docker rm $(sudo docker ps -a -q)

# Remove all images
#sudo docker rmi $(sudo docker images -q)

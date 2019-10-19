#!/usr/bin/env bash

systemctl status nginx
ip addr show eth0 | grep inet | awk '{ print $2; }' | sed 's/\/.*$//'


sudo ufw app list
sudo ufw allow 'Nginx HTTP'
sudo ufw status

sudo systemctl stop nginx
sudo systemctl start nginx
sudo systemctl restart nginx
sudo systemctl reload nginx
sudo systemctl disable nginx # don't start on boot
sudo systemctl enable nginx # start on boot

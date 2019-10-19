#!/usr/bin/env bash
# REFERENCE: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)
# FILE_DIR=/home/yerihyo/yeri/projects/lbox/henrique/scripts/uwsgi
DEPLOY_DIR=$(dirname $FILE_DIR)
SCRIPTS_DIR=$(dirname $DEPLOY_DIR)
REPO_DIR=$(dirname $SCRIPTS_DIR)

MAIN_DIR=$REPO_DIR/henrique/app/main
PROJECT_NAME=henrique

if [ "dev" == "$ENV" ]; then
    DOMAIN_NAME="dev.lbox.kr"
elif [ "production" = "$ENV" ]; then
    DOMAIN_NAME="lbox.kr"
else
    DOMAIN_NAME="localhost"
fi

errcho(){ >&2 echo $@; }

main(){
    FILEPATH_SOCK="$REPO_DIR/scripts/deploy/uwsgi/$PROJECT_NAME.sock"
    FILEPATH_SSL_CERTI="$REPO_DIR/env/ssl/ssl_certificate.pem"
    FILEPATH_SSL_PRIVATE_KEY="$REPO_DIR/env/ssl/ssl_private_key.pem"
    #FILEPATH_SOCK="/tmp/$PROJECT_NAME.sock"
    #FILEPATH_SOCK="/var/sockets/$PROJECT_NAME.sock"


    jinja2 $FILE_DIR/$PROJECT_NAME.tmplt \
        -D DOMAIN_NAME="$DOMAIN_NAME" \
        -D FILEPATH_SOCK="$FILEPATH_SOCK" \
        -D FILEPATH_SSL_CERTI="$FILEPATH_SSL_CERTI" \
        -D FILEPATH_SSL_PRIVATE_KEY="$FILEPATH_SSL_PRIVATE_KEY" \
        > $FILE_DIR/$PROJECT_NAME
}


errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"



# less /var/log/nginx/error.log  # checks the Nginx error logs.
# less /var/log/nginx/access.log  # checks the Nginx access logs.
# journalctl -u nginx  # checks the Nginx process logs.
# journalctl -u henrique  # checks your Flask app's uWSGI logs.

### ERROR / DEBUG (2019.09.17)
# SOCKET LEAKS
# https://www.nginx.com/resources/wiki/start/topics/tutorials/debugging/#socket-leaks
#
# > tail -f /var/log/nginx/error.log
#
# 2019/08/17 17:33:24 [alert] 24438#24438: *2 open socket #10 left in connection 3
# 2019/08/17 17:33:24 [alert] 24438#24438: aborting
#


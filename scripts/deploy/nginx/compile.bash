#!/usr/bin/env bash

#############
# REFERENCES
#
# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04
# https://towardsdatascience.com/how-to-do-rapid-prototyping-with-flask-uwsgi-nginx-and-docker-on-openshift-f0ef144033cb
#
# bad gateway 502 - https://stackoverflow.com/a/39117324
# uwsgi is not running.. or something similar... like socket filepath mismatch


ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)


errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)

PROJECT_NAME=henrique
#scheme=http
is_https=""
# USER=${USER?'missing $USER'}

if [[ "$ENV" == "local" || ! "$ENV" ]]; then
    DOMAIN_NAME="localhost"
else
    errcho "[$FILE_NAME] ERROR - \$ENV missing"
    exit 1
fi

main(){
    FILEPATH_SSL_CERTI="$REPO_DIR/env/ssl/ssl_certificate.pem"
    FILEPATH_SSL_PRIVATE_KEY="$REPO_DIR/env/ssl/ssl_private_key.pem"

    # https://github.com/mattrobenolt/jinja2-cli
    jinja2 $FILE_DIR/$PROJECT_NAME.nginx.conf.tmplt \
        -D DOMAIN_NAME="$DOMAIN_NAME" \
        -D REPO_DIR="$REPO_DIR" \
        -D NGINX_DIR="/usr/local/etc/nginx" \
        -D USER_GROUP="moon staff" \
        -D is_https="$is_https" \
        > $FILE_DIR/$PROJECT_NAME.nginx.local.conf

    jinja2 $FILE_DIR/$PROJECT_NAME.nginx.conf.tmplt \
        -D DOMAIN_NAME="$DOMAIN_NAME" \
        -D REPO_DIR="/app" \
        -D NGINX_DIR="/etc/nginx" \
        -D USER_GROUP="www-data www-data" \
        -D is_https="$is_https" \
        > $FILE_DIR/$PROJECT_NAME.nginx.docker.conf

#        -D USER="$USER" \

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


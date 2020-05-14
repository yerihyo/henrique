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


errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 3)

PROJECT_NAME=henrique
#scheme=http
is_https=""
USER=${USER?'missing $USER'}

if [[ "$ENV" == "local" || ! "$ENV" ]]; then
    DOMAIN_NAME="localhost"
else
    errcho "[$FILE_NAME] ERROR - \$ENV missing"
    exit 1
fi

main(){
    ENV=$ENV $FILE_DIR/compile.bash

    mkdir -p $REPO_DIR/log/nginx
    sudo nginx -s stop || errcho "no nginx running a priori"
    sudo nginx -g "daemon off;" -c $FILE_DIR/$PROJECT_NAME.nginx.local.conf
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


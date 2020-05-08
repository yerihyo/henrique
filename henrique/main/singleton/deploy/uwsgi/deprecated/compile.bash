#!/bin/bash -eu
# REFERENCE: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 4)

MAIN_DIR=$REPO_DIR/henrique/app/main
PROJECT_NAME=henrique

USERNAME=$(stat -c '%U' $FILE_PATH)
#GROUPNAME=$(stat -c '%G' $FILE_PATH)

mode2compile(){
    local mode="${1?missing 'mode'}"

}

main(){
    # files are already pre-compiled

    mkdir -p $REPO_DIR/log

    for mode in docker standalone; do
        jinja2 $FILE_DIR/$PROJECT_NAME.uwsgi.ini.tmplt \
            -D mode="$mode" \
            > "$FILE_DIR/ini/henrique.uwsgi.$mode.ini"
    done


}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"


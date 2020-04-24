#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 2)

FOXYLIB_DIR=${FOXYLIB_DIR?'missing $FOXYLIB_DIR'}

export SKIP_WARMUP=1
export FLASK_ENV=development
export FLASK_APP="henrique.main.run" #:create_app"
export ELASTICSEARCH_HOST="http://localhost:9200"

export PYTHONPATH=$FOXYLIB_DIR
export FLASK_RUN_PORT=14920

main(){
    flask run
#    python -m henrique.main.chatapp.discord.connect
}
# $REPO_DIR/henrique/scripts/run.bash >& $REPO_DIR/log/henrique.log &


pushd $REPO_DIR

errcho "[$FILE_NAME] start (REPO_DIR:$REPO_DIR)"
main
errcho "[$FILE_NAME] end (REPO_DIR:$REPO_DIR)"

popd

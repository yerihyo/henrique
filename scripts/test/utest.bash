#!/bin/bash -f

set -e
set -u

FILE_PATH=$(readlink -f $0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo $@; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

REPO_DIR=$(func_count2reduce $FILE_DIR dirname 2)

FOXYLIB_DIR=${FOXYLIB_DIR?'missing $FOXYLIB_DIR'}
pushd $REPO_DIR

export SKIP_WARMUP=1
export PYTHONPATH=$FOXYLIB_DIR

# python -m unittest henrique.main.hub.postgres.tests.test_postgres_hub.PostgresHubTest.test_01
# python -m unittest henrique.main.handlers.jinni.ask.tests.test_handler.TestHandler.test_03
python -m unittest henrique.main.skill.port.tests.test_port_skill.TestPortSkill

popd

#!/bin/bash -f

set -e
set -u

FILE_PATH=$(readlink -f $0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)
# FILE_DIR=`pwd`/../scripts/test
SCRIPTS_DIR=$FILE_DIR
REPO_DIR=$(dirname $SCRIPTS_DIR)

FOXYLIB_DIR=${FOXYLIB_DIR?'missing $FOXYLIB_DIR'}
pushd $REPO_DIR

export SKIP_WARMUP=1
export PYTHONPATH=$FOXYLIB_DIR

# python -m unittest henrique.main.hub.postgres.tests.test_postgres_hub.PostgresHubTest.test_01
python -m unittest henrique.main.handlers.jinni.ask.tests.test_handler.TestHandler.test_03

popd

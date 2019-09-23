#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

SCRIPTS_DIR=$(dirname $FILE_DIR)
REPO_DIR=$(dirname $SCRIPTS_DIR)

LPASS_DIR=$FILE_DIR

listfile_filepath=$($LPASS_DIR/tmplt2filelist.bash)
$FOXYLIB_DIR/scripts/lpass/pull.bash "$listfile_filepath"

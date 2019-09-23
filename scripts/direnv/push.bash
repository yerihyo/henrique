#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

SCRIPTS_DIR=$(dirname $FILE_DIR)
LPASS_DIR=$SCRIPTS_DIR/lpass

listfile_filepath=$($LPASS_DIR/tmplt2filelist.bash)
$HOME/scripts/direnv/push.bash "$listfile_filepath" "$@"


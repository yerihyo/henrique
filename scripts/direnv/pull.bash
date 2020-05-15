#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

SCRIPTS_DIR=$(dirname $FILE_DIR)
LPASS_DIR=$SCRIPTS_DIR/lpass

errcho(){ >&2 echo "$@"; }

errcho "[$FILE_NAME] START"

listfile_filepath=$($LPASS_DIR/tmplt2filelist.bash)
$FOXYLIB_DIR/scripts/direnv/pull.bash "$listfile_filepath" "$@"

errcho "[$FILE_NAME] END"

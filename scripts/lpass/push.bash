#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

LPASS_DIR=$FILE_DIR

listfile_filepath=$($LPASS_DIR/tmplt2filelist.bash)
$HOME/scripts/lpass/push.bash "$listfile_filepath"

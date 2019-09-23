#!/bin/bash -eu


ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_DIR=$(dirname $FILE_PATH)
FILE_NAME=$(basename $FILE_PATH)

yaml_dir=$($FILE_DIR/yaml_dir.bash)

echo "LASTPASS_ID: 4677762168923690061" > $yaml_dir/env.part.yaml
# echo "LASTPASS_ID: 2913436876351260056" > $yaml_dir/mkang.part.yaml
#!/bin/bash -eu

ARG0=${BASH_SOURCE[0]}
FILE_PATH=$(readlink -f $ARG0)
FILE_NAME=$(basename $FILE_PATH)
FILE_DIR=$(dirname $FILE_PATH)

errcho(){ >&2 echo "$@"; }
func_count2reduce(){
    local v="${1?missing}"; local cmd="${2?missing}"; local n=${3?missing};
    for ((i=0;i<$n;i++)); do v=$($cmd $v) ; done; echo "$v"
}

get_os(){
    if [ "$(uname)" == "Darwin" ]; then echo "macos";
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then echo "linux"
    elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then echo "win32"
    elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then echo "win64"
    else errcho "Invalid uname '$(name)'"; exit 1
    fi
}


REPO_DIR=$(func_count2reduce "$FILE_DIR" dirname 2)
SCRIPTS_DIR=$REPO_DIR/scripts
FOXYLIB_DIR=${FOXYLIB_DIR?"FOXYLIB_DIR missing"}

main(){
    pushd $REPO_DIR

    export ENV=local
    export PYTHONPATH=$FOXYLIB_DIR

    $FOXYLIB_DIR/scripts/direnv/init.bash "$REPO_DIR"
    . $SCRIPTS_DIR/virtualenv/activate.bash # this mess up with FOXYLIB_DIR somehow

    os=$(get_os)
    if [[ $os == "macos" && -s "$HOME/.bashrc" ]]; then
	. $HOME/.bashrc
    fi
    
    popd
}

errcho "[$FILE_NAME] START"
main
errcho "[$FILE_NAME] END"


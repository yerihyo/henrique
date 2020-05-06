#!/bin/bash 

set -e
set -u

FILE_DIR=$(dirname `readlink -f ${0}`)
# FILE_DIR=`pwd`/../scripts

branch=`git branch | grep '\*' | awk '{print $2}'`
target=master

git push origin $branch
git checkout $target
git merge --no-ff $branch
git push origin $target
git checkout $branch

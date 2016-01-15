#!/bin/bash

set -ex

REPO="git@github.com:contentful-labs/contentful.py.git"
DIR=sphinx_tmp
ROOT=`pwd`

function cleanup {
    cd ${ROOT}/docs
    make clean
    rm -rf ${DIR}
    cd ../
}

trap cleanup EXIT
cd docs
make clean html
rm -rf ${DIR}
git clone ${REPO} ${DIR}
cd ${DIR}
git checkout -t origin/gh-pages
rm -rf *
cp -R ../_build/html/* .
git add .
git add -u
git commit -m "Documentation at $(date)"
git push origin gh-pages
cd ../..

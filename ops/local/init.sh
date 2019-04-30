#!/usr/bin/env bash

SCRIPT_HOME=$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)
ROOT_DIR=${SCRIPT_HOME}/../../..


#sudo unlink /app/contracts
#sudo ln -sf ${PWD}/contracts /app/contracts

python3 -m venv .zenroom-tp.venv
. ./.zenroom-tp.venv/bin/activate
pip install --upgrade pip
pip install -e .


echo "If you are on OSX you will maybe need to install a custom version of zenroom with osx lib in it"
echo "(in virtual env) pip install ../zenroom-py/dist/zenroom-0.1.3.tar.gz "


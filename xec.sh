#!/usr/bin/env bash

# This is an entry point for all the bash scripting that we provide with this module
# We also provide a makefile with some convenient shortcuts, but everything can be done from here for more fine grained control

#set -e # Exit script if anything fails
set -u # unset variables cause an error
set -o pipefail # https://coderwall.com/p/fkfaqq/safer-bash-scripts-with-set-euxo-pipefail
#set -x # for debugging each command

source ops/_lib/lib.sh

function install {
    echo -e "'nInstalling 'xec' alias so you just have to type 'xec ...' instead of './xec.sh' ...\n"
    alias xec="./xec.sh"
    echo -e "\nIf you want this permanently just add it to your '.bashrc' file\n"

}

function docker {
    ./ops/local/docker.sh $@
}

function init {
    docker init
}

function up {
    docker up
}

function down {
    docker down
}

function status {
    docker status
}

function logs {
    docker logs
}

function service {
    ./ops/local/docker_service.sh $@
}

function zenroom-tp {
    service zenroom-tp $@
}

function validator {
    service validator $@
}

function shell {
    echo -e "Attaching to a container for executing sawtooth commands ...\n"
    service shell shell
}

function petition {
    source ./.zenroom-tp.venv/bin/activate && ${PWD}/scripts/execute_petition.py
}

lib/process_commands $@

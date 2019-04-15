#!/usr/bin/env bash

set -e # Exit script if anything fails
set -u # unset variables cause an error
set -o pipefail # https://coderwall.com/p/fkfaqq/safer-bash-scripts-with-set-euxo-pipefail
#set -x # for debugging each command

SCRIPT_HOME=$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)

source ${SCRIPT_HOME}/../_lib/env.sh


function init {
    ${DOCKER_COMMAND} up --no-start --build

}

function up {
    ${DOCKER_COMMAND} up --detach
}

function down {
    ${DOCKER_COMMAND} down
}

function status {
    echo -e "Status of local docker network:"
    echo -e "Docker Config: ${DOCKER_COMPOSE_CONFIG}\n"


    ${DOCKER_COMMAND} ps
}

function logs {
    ${DOCKER_COMMAND} logs --follow
}

lib/process_commands $@

#!/usr/bin/env bash

set -e # Exit script if anything fails
set -u # unset variables cause an error
set -o pipefail # https://coderwall.com/p/fkfaqq/safer-bash-scripts-with-set-euxo-pipefail
#set -x # for debugging each command

SCRIPT_HOME=$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)

source ${SCRIPT_HOME}/../_lib/env.sh


CHAINSPACE_API_URL="http://localhost:5000/api/1.0/"

SERVICE_NAME=$1
shift

function status {

    echo -e "Status of local service [${SERVICE_NAME}]:\n"
    echo -e "Docker Config: \n${DOCKER_COMPOSE_CONFIG}\n"
    ${DOCKER_COMMAND} ps ${SERVICE_NAME}

    HTTP_STATUS=$(lib/http_status_of ${CHAINSPACE_API_URL})

    echo -e "\nStatus of local chainspace api @ ${CHAINSPACE_API_URL}: ${HTTP_STATUS}\n"
}

# TODO: Invert following so have to pass a --no-follow if you dont want folowo
function logs {
    ${DOCKER_COMMAND} logs --follow ${SERVICE_NAME}
}

function start {
    echo -e "\nStarting local docker container with ${SERVICE_NAME} (run [${SCRIPT_HOME}/docker_service.sh docker-logs] to see details)\n"
    ${DOCKER_COMMAND} start ${SERVICE_NAME}
    lib/wait_for_service ${CHAINSPACE_API_URL}
    status
}

function stop {
    echo "Stopping local ${SERVICE_NAME} docker container ...\n"
    ${DOCKER_COMMAND} stop ${SERVICE_NAME}
    echo -e "\${SERVICE_NAME} stopped."
}

function restart {
    echo "Restarting local  docker container ...\n"
    ${DOCKER_COMMAND} restart
    echo -e "${SERVICE_NAME} stopped."
}

function shell {
    ${DOCKER_COMMAND} exec ${SERVICE_NAME} bash
}

function rebuild {
   ${DOCKER_COMMAND} build ${SERVICE_NAME}
   ${DOCKER_COMMAND} restart ${SERVICE_NAME}
}

lib/process_commands $@

#!/usr/bin/env bash

SCRIPT_HOME=$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)

CLUSTER_NAME="sawtooth-tp-zenroom"

DOCKER_COMPOSE_CONFIG=${SCRIPT_HOME}/../../docker-compose.yaml
DOCKER_COMMAND="docker-compose -f ${DOCKER_COMPOSE_CONFIG}"

source ${SCRIPT_HOME}/lib.sh



#!/usr/bin/env bash

# https://stackoverflow.com/questions/59895/getting-the-source-directory-of-a-bash-script-from-within
# https://www.ostricher.com/2014/10/the-right-way-to-get-the-directory-of-a-bash-script/
# http://mywiki.wooledge.org/BashFAQ/031
# http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO-3.html - redirections

# TODO: make it so you have to prefix the commands with cmd_ or something so not all functions are availbale
function lib/process_commands {
    CMD=$1
    shift
    ${CMD} $@
}

function lib/ps {
    PROCESS_PATTERN=$1
    echo $(ps aux | grep ${PROCESS_PATTERN} | grep -v grep | cut -c1-80)
}

# https://stackoverflow.com/questions/11231937/bash-ignoring-error-for-a-particular-command
# -o makes the output disappear, -s means silent so it doesnt show you what download status
function lib/http_status_of {
    URL=$1
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}\n" ${URL} || true)
    if [[ ${HTTP_STATUS} == 200 ]]; then
        echo "Running (200 ok)"
    else
        echo "Not running (${HTTP_STATUS})"
    fi
}

function lib/wait_for_service {
  HOST=$1
  ATTEMPTS=0
  echo -e "\nWaiting for service to appear @ ${HOST} ...\n"
  while :
  do
    echo "Trying to reach ${HOST} [${ATTEMPTS}] ..."
    HTTP_STATUS=$(lib/http_status_of ${HOST})
    if [[ ${HTTP_STATUS} == "Running (200 ok)" ]]; then
      echo "Service @ ${HOST} is available"
      break;
    fi
    ((ATTEMPTS++))
    if [[ ${ATTEMPTS} == 15 ]]; then
      echo "The service ${HOST} is still not available after 15 retries"
      echo "Exiting"
      exit 1
    fi
    sleep 2
  done
}

function lib/command_exists {
    CMD=$1
    INSTRUCTIONS=$2
    command -v ${CMD} >/dev/null 2>&1 || { echo >&2 -e "\n[ERROR] This script requires the command '${CMD}' but it's not installed. ${INSTRUCTIONS}.  Exiting.\n"; exit 1; }
}
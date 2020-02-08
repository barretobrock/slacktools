#!/usr/bin/env bash
# Updates both the python package and the local git repo

# SETUP
# --------------
# ARGS
REPO=slacktools
INSTALL_SPEED=${1:-full}    # Full, won't skip dependencies on pip install, fast will

NODEPS_FLAG=''
if [[ "${INSTALL_SPEED}" == "fast" ]];
then
    echo "Not pip installing dependencies"
    NODEPS_FLAG="--no-deps"
fi

BLUE="\e[34m"
RESET="\e[0m"
announce_section () {
    # Makes sections easier to see in output
    SECTION_BRK="\n==============================\n"
    SECTION="${1}"
    printf "${BLUE}${SECTION_BRK}${SECTION}${SECTION_BRK}${RESET}"
}

# DIRECTORY SETUP
# CD to the location of the package and pull from master
ST_DIR=${HOME}/extras/${REPO}

# GIT PULL
# --------------
announce_section "Pulling update from git repo"
# TODO see if I can check if master is up to date before issuing command. If it is, don't pull
(cd ${ST_DIR} && git pull origin master)

# PY PACKAGE UPDATE
# --------------
# Then update the python package locally
announce_section "Beginning update of python package"
# TODO check if installed, then upgrade if so
python3 -m pip install git+https://github.com/barretobrock/${REPO}.git#egg=${REPO} --upgrade ${NODEPS_FLAG}

announce_section "Process completed"

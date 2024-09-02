#!/bin/bash

# REBOOT Variable
img_reboot=${1:-1}

# OTHER VARIABLES
KARMA_IMAGES=("karma_api" "karma_db" "karma_model")
CONTAINER_NAMES=("karma_api" "karma_db" "karma_model")
CURRENT_USER=$(whoami)

# ARGUMENT LIST FOR EACH DOCKER IMAGE
declare -A BUILD_ARGS
BUILD_ARGS["karma_api"]="SECRET_JWT_KEY=SECRET_JWT_KEY MYSQL_ROOT_PASSWORD=MYSQL_ROOT_PASSWORD_PROD"
BUILD_ARGS["karma_db"]="MYSQL_ROOT_PASSWORD=MYSQL_ROOT_PASSWORD_PROD"

# DOCKER PREREQUISITES
echo "...:: Démarrage de Docker"
if [ -x "$(command -v docker)" ]; then
    echo "Docker installed. Docker start handling..."
        # Check if Docker is running to avoid password sudo prompt
        if docker info >/dev/null 2>&1; then
            echo "Docker already running"
        else
            echo "Docker not running. Start attempt, user password needed..."
            sudo service docker start

            # Check if Docker properly started
            if docker info >/dev/null 2>&1; then
                echo "Docker started"
            else
                echo "Docker start failed, please check your install"
            fi
        fi
else
    echo "Docker not installed, follow instructions on : https://docs.docker.com/engine/install/"
    exit 1
fi

# IMAGES HANDLING IF REBOOT : REMOVE IF EXIST FOR EACH
echo "...:: Images Reboot Mode handling"
if [ "$img_reboot" -eq 1 ]; then
    for KARMA_IMAGE in "${KARMA_IMAGES[@]}"; do
        if docker image ls | grep -q "${KARMA_IMAGE}"; then
            echo "Reboot Option Activated : Existing '${KARMA_IMAGE}' image remove..."
            docker image rm $KARMA_IMAGE:latest
        fi
    done
fi

# IMAGES HANDLING BUILD
echo "...:: Images build handling"
for KARMA_IMAGE in "${KARMA_IMAGES[@]}"; do
    echo "...:: ${KARMA_IMAGE} docker image"
    if docker image ls | grep -q "${KARMA_IMAGE}"; then
        echo "Image '${KARMA_IMAGE}' already exists"
    else
        echo "Image build '$KARMA_IMAGE'"
        BUILD_CMD="docker image build"
        IFS=' ' read -ra ARGS <<< "${BUILD_ARGS[$KARMA_IMAGE]}"
        for ARG_PAIR in "${ARGS[@]}"; do
            IFS='=' read -ra PAIR <<< "$ARG_PAIR"
            ARG=${PAIR[0]}
            VAR=${PAIR[1]}
            if [ -f ignore/secret.env ]; then
                BUILD_CMD+=" --build-arg $ARG=$(grep $VAR ignore/secret.env | cut -d '=' -f2)"
            else
                BUILD_CMD+=" --build-arg $ARG=${!VAR}"
            fi
        done
        echo $RELEASE_TAG
        TAG=${RELEASE_TAG:-latest}
        echo "RELEASE TAG PLACE"
        echo $TAG
        # BUILD_CMD+=" -f docker/${KARMA_IMAGE}/Dockerfile.prod -t avr24rakuten/${KARMA_IMAGE}:${TAG} ."
        BUILD_CMD+=" -f docker/${KARMA_IMAGE}/Dockerfile.prod -t avr24rakuten/${KARMA_IMAGE}:latest ."
        eval $BUILD_CMD || { echo "Image creation failed"; exit 1; }
    fi
done
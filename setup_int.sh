#!/bin/bash

# REBOOT Variable
img_reboot=${1:-0}

# OTHER VARIABLES
KARMA_IMAGES=("karma_api" "karma_db" "karma_model")
CONTAINER_NAMES=("karma_api" "karma_db" "karma_model")
CURRENT_USER=$(whoami)

# ARGUMENT LIST FOR EACH DOCKER IMAGE
declare -A BUILD_ARGS
BUILD_ARGS["karma_api"]="SECRET_JWT_KEY=SECRET_JWT_KEY MYSQL_ROOT_PASSWORD=MYSQL_ROOT_PASSWORD_INT"
BUILD_ARGS["karma_db"]="MYSQL_ROOT_PASSWORD=MYSQL_ROOT_PASSWORD_INT"

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

# DOCKER COMPOSE PREREQUISITES
echo "...:: Contrôle de Docker Compose"
if [ -x "$(docker-compose --version)" ]; then
    echo "Docker Compose installed ..."
else
    echo "Docker Compose not installed, follow instructions on : https://docs.docker.com/compose/install/"
    exit 1
fi


echo "...:: Containers status check and stop if needed"
# For each container in upper list
for CONTAINER_NAME in "${CONTAINER_NAMES[@]}"; do

  # Check if container exists
  if [ $(docker ps -a -f name=$CONTAINER_NAME | grep -w $CONTAINER_NAME | wc -l) -gt 0 ]; then
    echo "Container $CONTAINER_NAME exists"

    # Check if container is running
    if [ $(docker ps -f name=$CONTAINER_NAME | grep -w $CONTAINER_NAME | wc -l) -gt 0 ]; then
      echo "Container $CONTAINER_NAME is running, stop it ..."
      docker stop $CONTAINER_NAME || { echo "Stop container $CONTAINER_NAME failed"; exit 1; }
    fi

    echo "Container $CONTAINER_NAME remove..."
    docker rm $CONTAINER_NAME || { echo "Container $CONTAINER_NAME remove failed"; exit 1; }

    echo "Container $CONTAINER_NAME removed"
  else
    echo "Container $CONTAINER_NAME doesn't exist"
  fi
done

# VOLUME HANDLING
echo "...:: Suppression/Creation du volume"
if docker volume ls | grep -q 'karma_shared_volume'; then
    echo "Volume karma_shared_volume already exists and will be removed"
    docker volume rm karma_shared_volume
fi
echo "karma_shared_volume Volume creation"
if [ -f ignore/secret.env ]; then
    docker volume create --driver local --opt type=none --opt device=/home/$CURRENT_USER/karma/shared/ --opt o=bind karma_shared_volume || { echo "karma_shared_volume Volume creation failed"; exit 1; }
else
    docker volume create --driver local --opt type=none --opt device=/home/$CURRENT_USER/work/karma/karma/shared/ --opt o=bind karma_shared_volume || { echo "karma_shared_volume Volume creation failed"; exit 1; }
fi 


# NETWORK CREATION IF NEEDED
echo "...:: Suppression/Creation du network"
if docker network ls | grep -q 'karma_network'; then
    echo "Network karma_network already exists"
else
    echo "karma_network Network creation"
    docker network create karma_network || { echo "karma_network Network creation failed"; exit 1; }
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
        BUILD_CMD+=" -f docker/${KARMA_IMAGE}/Dockerfile.int -t ${KARMA_IMAGE}:latest ."
        eval $BUILD_CMD || { echo "Image creation failed"; exit 1; }
    fi
done

# LAUNCH DOCKER COMPOSE
echo "...:: Docker compose start..."
docker compose -f docker/docker-compose-karma-int.yml up -d
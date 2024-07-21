#!/bin/bash

# REBOOT Variable
img_reboot=${1:-0}

# OTHER VARIABLES
KARMA_IMAGES=("karma_api" "karma_db" "karma_model")
CONTAINER_NAMES=("karma_api" "karma_db" "karma_model")

# DOCKER PREREQUISITES
echo "...:: Démarrage de Docker"
if [ -x "$(command -v docker)" ]; then
    echo "Docker est installé. Démarrage de Docker..."
    # PAS BESOIN DE CHECKER S'il EST DEJA LANCE
    sudo service docker start
else
    echo "Docker n'est pas installé, vous pouvez suivre les instructions disponibles : https://docs.docker.com/engine/install/"
    exit 1
fi

# DOCKER COMPOSE PREREQUISITES
echo "...:: Contrôle de Docker Compose"
if [ -x "$(command -v docker)" ]; then
    echo "Docker Compose est installé ..."
else
    echo "Docker Compose n'est pas installé, vous pouvez suivre les instructions disponibles : https://docs.docker.com/compose/install/"
    exit 1
fi

# VOLUME HANDLING
echo "...:: Suppression/Creation du volume"
    docker volume rm karma_shared_volume
    docker volume create --driver local --opt type=none --opt device=~/karma/shared/ --opt o=bind karma_shared_volume

# NETWORK CREATION IF NEEDED
if docker network ls | grep -q 'karma_network'; then
    echo "Network karma_network already exists"
else
    echo "karma_network Network creation"
    docker create network karma_network || { echo "karma_network Network creation failed"; exit 1; }
fi

echo "...:: Containers status check"
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


# IMAGES HANDLING
for KARMA_IMAGE in "${KARMA_IMAGES[@]}"; do
    echo "...:: ${KARMA_IMAGE} docker image"
    if docker image ls | grep -q "${KARMA_IMAGE}"; then
        echo "Image '${KARMA_IMAGE}' already exists"
        if [ "$img_reboot" -eq 1 ]; then
            echo "Reboot Option Activated : Existing image remove..."
            docker image rm $KARMA_IMAGE:latest
            if [ "$KARMA_IMAGE" = "karma_api" ]; then
                docker image build --build-arg SECRET_JWT_KEY=$(grep SECRET_JWT_KEY ~/karma/ignore/secret.env | cut -d '=' -f2) -f ~/karma/docker/${KARMA_IMAGE}/Dockerfile.int -t ${KARMA_IMAGE}:latest . || { echo "Image creation failed"; exit 1; } 
            else
                docker image build -f ~/karma/docker/${KARMA_IMAGE}/Dockerfile.int -t ${KARMA_IMAGE}:latest . || { echo "Image creation failed"; exit 1; } 
            fi
        fi
    else
        echo "Image build '$KARMA_IMAGE'"
        if [ "$KARMA_IMAGE" = "karma_api" ]; then
            docker image build --build-arg SECRET_JWT_KEY=$(grep SECRET_JWT_KEY ~/karma/ignore/secret.env | cut -d '=' -f2) -f ~/karma/docker/${KARMA_IMAGE}/Dockerfile.int -t ${KARMA_IMAGE}:latest . || { echo "Image creation failed"; exit 1; } 
        else
            docker image build -f ~/karma/docker/${KARMA_IMAGE}/Dockerfile.int -t ${KARMA_IMAGE}:latest . || { echo "'$KARMA_IMAGE' image creation failed"; exit 1; } 
        fi
    fi
done


# LAUNCH DOCKER COMPOSE, FastAPI en -d 
echo "...:: Docker compose start..."
docker-compose -f docker/docker-compose-karma-int.yml up -d
#!/bin/bash

### ### PARAMETERS
if [ -z "$1" ]; then
  echo "Missing : $0 <version>"
  exit 1
fi

VERSION=$1

### ### V1 WITHOUT ROLL

### KARMA DB DUMP IN SHARED IF EXIST


### BEFORE DOCKER TESTS

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

### DOCKER DEPLOYMENT WITH DOCKER COMPOSE
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
docker volume create --driver local --opt type=none --opt device=/home/$CURRENT_USER/karma/shared/ --opt o=bind karma_shared_volume || { echo "karma_shared_volume Volume creation failed"; exit 1; }

# NETWORK CREATION IF NEEDED
echo "...:: Suppression/Creation du network"
if docker network ls | grep -q 'karma_network'; then
    echo "Network karma_network already exists"
else
    echo "karma_network Network creation"
    docker network create karma_network || { echo "karma_network Network creation failed"; exit 1; }
fi

# IMAGES HANDLING IF REBOOT : REMOVE IF EXIST FOR EACH
echo "...:: Images Remove images handling"
for KARMA_IMAGE in "${KARMA_IMAGES[@]}"; do
    if docker image ls | grep -q "${KARMA_IMAGE}"; then
        echo "Existing '${KARMA_IMAGE}' image remove..."
        docker image rm $KARMA_IMAGE:latest
    fi
done

echo "...:: Docker compose start..."

sed "s/__VERSION__/$VERSION/g" docker/docker-compose-template.yml > docker/docker-compose-karma-prod.yml

docker compose -f docker/docker-compose-karma-prod.yml up -d

### KARMA DB RESTORE IN SHARED IF EXIST


### ### V2 WITH KUBERNETES ROLL

# SAUVEGARDE DE LA DB KARMA DANS KARMA_DB IF EXIST



# KUBERNETES ROLL DES 3 CONTAINERS
# kubectl apply -f karma_secret.yml
# kubectl apply -f karma_api_service.yml
# kubectl apply -f karma_api_ingress.yml
# kubectl apply -f karma_api_deployment.yml
# kubectl apply -f karma_db_statefulset.yml
# kubectl apply -f karma_db_service.yml
# # kubectl apply -f karma_db_deployment.yml
# kubectl apply -f karma_model_deployment.yml
# kubectl apply -f karma_shared_pvc.yml

# RESTAURATION DE LA DB



# TESTS
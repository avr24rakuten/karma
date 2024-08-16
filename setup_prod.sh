#!/bin/bash

# SAUVEGARDE DE LA DB KARMA DANS KARMA_DB IF EXIST



# KUBERNETES ROLL DES 3 CONTAINERS
kubectl apply -f karma_secret.yml
kubectl apply -f karma_api_service.yml
kubectl apply -f karma_api_ingress.yml
kubectl apply -f karma_api_deployment.yml
kubectl apply -f karma_db_statefulset.yml
kubectl apply -f karma_db_service.yml
# kubectl apply -f karma_db_deployment.yml
kubectl apply -f karma_model_deployment.yml
kubectl apply -f karma_shared_pvc.yml

# RESTAURATION DE LA DB



# TESTS
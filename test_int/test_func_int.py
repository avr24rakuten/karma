import pytest
import os
import json
import sys
import requests

from lib.utils import *

try:
    host_ip = os.environ.get('HOST_IP')
except:
    print("HOST IP not in HOST_IP Env variable") 
    sys.exit(1)

try:
    token_admin = get_admin_token(host_ip)
except:
    print("Not Admin Token acquired") 
    sys.exit(1)

#############################################
# STATUS & HEALTHCHECK
#############################################

def test_get_karma_healthcheck():
    response = requests.get('http://{}:8000/karma_healthcheck'.format(host_ip))
    assert response.status_code == 200

#############################################
# LOGIN
#############################################

def test_get_login_ok():
    url = "http://{}:8000/users/login".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "username": "admin",
        "password": "YWRtaW4=",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)  # Vérifie que le token est une chaîne de caractères
    assert data["token_type"] == "bearer"

def test_get_login_ko_not64base():
    url = "http://{}:8000/users/login".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "username": "admin",
        "password": "YWRtaW=",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 400
    assert response.json() == {"detail":"String is not properly base64 & utf-8 encoded"}

def test_get_login_ko_wrongpassword():
    url = "http://{}:8000/users/login".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "username": "admin",
        "password": "YWRtaQ==",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 401
    assert response.json() == {"detail":"Incorrect username or password"}

#############################################
# PREDICT
#############################################



#############################################
# USERS
#############################################

def test_delete_user_ok():
    url = "http://{}:8000/users/delete".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_admin),
    }

    response = requests.delete(url, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"detail":"User delete successfully deleted"}

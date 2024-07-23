import pytest
import os
import json
import sys
import requests

try:
    host_ip = os.environ.get('HOST_IP')
except:
    print("HOST IP not in HOST_IP Env variable") 
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

#############################################
# PREDICT
#############################################



#############################################
# USERS
#############################################
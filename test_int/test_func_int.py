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
    token_reader = get_reader_token(host_ip)
except:
    print("Not Token acquired") 
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
    assert isinstance(data["access_token"], str)
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

# PREDICT WITH FORM AND INPUTFILE INPUT
def test_products_predict_ok():

    url = "http://{}:8000/products/predict".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_reader),
    }
    data = {
    "description": ("", "Olivia: Personalisiertes Notizbuch / 150 Seiten / Punktraster / Ca Din A5 / Rosen-Design"),
    "image": open("/home/hymnuade/karma/shared/image_1263597046_product_3804725264.jpg", "rb")
}
    response = requests.post(url, headers=headers, files=data)


    # CREATE ASSERT
    assert response.status_code == 200
    assert response['prediction'][0] == 1234


#############################################
# USERS
#############################################

# CREATE USER
def test_create_user_ok():
    user = 'test'
    password = 'dGVzdA=='
    url = "http://{}:8000/users".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_admin),
    }
    data = {
        "user": user,
        "password": password,
        "roles": {
            "admin": False,
            "steward": False,
            "reader": False
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    check_url = "http://{}:8000/users/login".format(host_ip)
    check_headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    check_data = {
        "username": user,
        "password": password,
    }
    check_response = requests.post(check_url, headers=check_headers, data=json.dumps(check_data))

    # CREATE ASSERT
    assert response.status_code == 200
    assert response.json() == {"detail":"User successfully created"}
    # LOGIN CALL ASSERT
    assert check_response.status_code == 200


def test_create_user_not_ok():
    url = "http://{}:8000/users".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_reader),
    }
    data = {
        "user": "test",
        "password": "dGVzdA==",
        "roles": {
            "admin": False,
            "steward": False,
            "reader": False
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 403
    assert response.json() == {"detail":"Insufficient role"}

def test_create_user_no_privilege():
    url = "http://{}:8000/users".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_admin),
    }
    data = {
        "user": "test",
        "password": "dGVzdA==",
        "roles": {}
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 400
    assert response.json() == {"detail":"One privilege at least is required for user creation"}

def test_create_user_no_password():
    url = "http://{}:8000/users".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_admin),
    }
    data = {
        "user": "test",
        "roles": {
            "admin": False,
            "steward": False,
            "reader": False
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 400
    assert response.json() == {"detail":"Password is mandatory"}

# CREATE USER READER BY DEFAULT

def test_create_user_reader_ok():
    user = 'test_reader'
    password = 'dGVzdF9yZWFkZXI='
    url = "http://{}:8000/users/reader".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "user": "{}".format(user),
        "password": "{}".format(password)
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    check_url = "http://{}:8000/users/login".format(host_ip)
    check_headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    check_data = {
        "username": user,
        "password": password
    }
    check_response = requests.post(check_url, headers=check_headers, data=json.dumps(check_data))

    # CREATE ASSERT
    assert response.status_code == 200
    assert response.json() == {"detail":"User successfully created"}
    # LOGIN CALL ASSERT
    assert check_response.status_code == 200

def test_create_user_reader_no_password():
    url = "http://{}:8000/users/reader".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "user": "test_reader"
        }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 400
    assert response.json() == {"detail":"Password is mandatory"}

# MODIFY USER
def test_update_user_ok():
    url = "http://{}:8000/users".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_admin),
    }
    data = {
        "user": "test",
        "roles": {
            "admin": False,
            "steward": False,
            "reader": True
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    assert response.json() == {"detail":"User successfully updated"}

def test_update_user_not_ok():
    url = "http://{}:8000/users".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_reader),
    }
    data = {
        "user": "test",
        "roles": {
            "admin": False,
            "steward": False,
            "reader": False
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 403
    assert response.json() == {"detail":"Insufficient role"}

def test_update_user_bad_data():
    url = "http://{}:8000/users".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_admin),
    }
    data = {
        "user": "test",
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    assert response.status_code == 400
    assert response.json() == {"detail":"One role at least is required for user update"}

# DELETE USER
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

def test_delete_user_not_ok():
    url = "http://{}:8000/users/delete".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_reader),
    }
    response = requests.delete(url, headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail":"Insufficient role"}

def test_delete_user_not_exist():
    url = "http://{}:8000/users/dele".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token_admin),
    }
    response = requests.delete(url, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail":"Resources not found"}

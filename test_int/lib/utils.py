import json
import requests

def get_admin_token(host_ip):
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
    return response.json()["access_token"]

def get_reader_token(host_ip):
    url = "http://{}:8000/users/login".format(host_ip)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "username": "reader",
        "password": "cmVhZGVy",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()["access_token"]

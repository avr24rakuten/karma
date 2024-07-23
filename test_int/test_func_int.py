import pytest
import os
import sys
import requests

# from lib.mysql import *

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



#############################################
# PREDICT
#############################################



#############################################
# USERS
#############################################
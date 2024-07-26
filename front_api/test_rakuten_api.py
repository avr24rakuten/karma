import pytest
from fastapi import HTTPException
from typing import Dict
from pydantic import BaseModel, ValidationError

from lib.security import *
from lib.local_class import *

#############################################
# SECURITY UNIT TEST PART
#############################################

# decode_base64
def test_decode_base64_ok():
    res = decode_base64('YWRtaW4=')
    assert res == 'admin'

def test_decode_base64_error_nonascii():
    with pytest.raises(HTTPException) as excinfo:
        decode_base64('non-ascïî:é')
    assert excinfo.value.status_code == 400

def test_decode_base64_error_nonbase64encoded():
    with pytest.raises(HTTPException) as excinfo:
        decode_base64('admin')
    assert excinfo.value.status_code == 400

def test_decode_base64_error_nonutf8encoded():
    str_non_utf8 = "adminaaa".encode('latin-1')
    str_non_utf8_base64 = base64.b64encode(str_non_utf8)
    with pytest.raises(HTTPException) as excinfo:
        decode_base64(str_non_utf8_base64)
    assert excinfo.value.status_code == 400


#############################################
# LOCAL CLASS
#############################################

def test_input_user_initialization():
    user = "test_user"
    password = "test_password"
    roles = {"admin": True}

    input_user = InputUser(user=user, password=password, roles=roles)

    assert input_user.user == user
    assert input_user.password == password
    assert input_user.roles == roles

def test_input_user_invalid_roles():
    user = "test_user"
    password = "test_password"
    roles = {"admin": "not a boolean"}

    with pytest.raises(ValidationError):
        input_user = InputUser(user=user, password=password, roles=roles)
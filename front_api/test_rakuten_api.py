import pytest
from fastapi import HTTPException
from typing import Dict
from pydantic import BaseModel, ValidationError

from lib.security import *
from lib.local_class import *

#############################################
# LIB.SECURITY UNIT TEST PART
#############################################

# FUNCTION : create_access_token

ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
SECRET_JWT_KEY = os.environ['SECRET_JWT_KEY']

def test_create_access_token():
    # Simple dict test
    data = {"sub": "admin"}
    token = create_access_token(data)
    # Token decode
    decoded_token = jwt.decode(token, SECRET_JWT_KEY, algorithms=[ALGORITHM])
    # Correct encoding in Token
    assert decoded_token["sub"] == data["sub"]
    # Check if Token expire in ACCESS_TOKEN_EXPIRE_MINUTES
    assert datetime.fromtimestamp(decoded_token["exp"], timezone.utc) - datetime.now(timezone.utc) <= timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

def test_create_access_token_invalid_type():
    # Non-dict parameter test
    with pytest.raises(AttributeError):
        create_access_token("not a dict")

# FUNCTION : decode_base64
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

# FUNCTION : encode_base64
def test_encode_base64():
    # Simple string test
    assert encode_base64("test") == base64.b64encode("test".encode()).decode()

    # More complkex string test
    assert encode_base64("Ceci est un test plus complexe.") == base64.b64encode("Ceci est un test plus complexe.".encode()).decode()

    # Special characters test
    assert encode_base64("@#$$%^&*()!") == base64.b64encode("@#$$%^&*()!".encode()).decode()

    # Empty string test
    assert encode_base64("") == base64.b64encode("".encode()).decode()

def test_encode_base64_invalid_type():
    # Invalid type test
    with pytest.raises(AttributeError):
        encode_base64(123)

#############################################
# LIB.LOCAL CLASS
#############################################

# CLASS : InputUser
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

# CLASS : User
def test_user_initialization():
    user = User(user_id=1, user="test_user", hashed_password="hashed_password", admin=True, steward=False, reader=True)

    assert user.user_id == 1
    assert user.user == "test_user"
    assert user.hashed_password == "hashed_password"
    assert user.admin == True
    assert user.steward == False
    assert user.reader == True

def test_user_invalid_role_type():
    with pytest.raises(ValidationError):
        user = User(user_id=1, user="test_user", hashed_password="hashed_password", admin="not a boolean", steward=False, reader=True)


# FUNCTION : convert_user_to_input_user
def test_convert_user_to_input_user():
    user = User(user_id=1, user="test_user", hashed_password="hashed_password", admin=True, steward=False, reader=True)

    input_user = convert_user_to_input_user(user)

    assert input_user.user == user.user
    assert input_user.password == user.hashed_password
    assert input_user.roles == {'admin': user.admin, 'steward': user.steward, 'reader': user.reader}
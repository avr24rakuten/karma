from datetime import timedelta, timezone, datetime
from sqlalchemy import text
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from typing_extensions import Annotated
from fastapi import HTTPException, status, Depends
import os
import base64
import re
import binascii


from lib.mysql import *
from lib.local_class import *
from lib.api_exception import *
from shared.lib.utils import *

# GET ALL NEEDED KARMA ENV VARIABLE
EnvLoader.load_env()

ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_JWT_KEY = os.environ['SECRET_JWT_KEY']


# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 1440

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_user(user: str):
    engine = get_engine()
    with engine.connect() as connection:
        statement = text('SELECT * FROM users WHERE users.user = '':user'' LIMIT 1')
        results = connection.execute(statement,{"user": user})

    result = results.fetchone()
    if result is not None:
        user = User(
            user_id=result[0],
            user=result[1],
            hashed_password=result[2],
            admin=result[3],
            steward=result[4],
            reader=result[5]
        )
    else:
        user = None

    return user

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not check_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_JWT_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(user=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_admin(user: User = Depends(get_current_user)):
    if not user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role"
        )
    return user

# PAs très générique si on ajoute un rôle, approche à revoir !!!!
def get_any_role(user: User = Depends(get_current_user)):
    if not user.admin and not user.steward and not user.reader:
        # raise InsufficientPrivilege(
        #     name='Insufficient privilege',
        #     date=str(datetime.now())
        # )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role"
        )
    return user

def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Password hash with salt
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()

def check_password(password, hashed_password):
    try:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
    except ValueError:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + access_token_expires
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_JWT_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def encode_base64(str_variable):
    str_variable_bytes = str_variable.encode('utf-8')
    str_variable_base64 = base64.b64encode(str_variable_bytes)
    return str_variable_base64.decode('utf-8')

def decode_base64(str_variable_base64):
    try:
        str_variable_base64_bytes = str_variable_base64.encode('utf-8')
        str_variable_bytes = base64.b64decode(str_variable_base64_bytes)
        return str_variable_bytes.decode('utf-8')   
    except:
        raise HTTPException(status_code=400, detail="String is not properly base64 & utf-8 encoded")
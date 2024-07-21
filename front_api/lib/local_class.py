from pydantic import BaseModel
from typing import Union, Dict, Optional

class InputUser(BaseModel):
    user: str
    password: str
    roles: Dict[str, bool]

class LoginUser(BaseModel):
    username: str
    password: str

class User(BaseModel):
    user_id : int
    user : str
    hashed_password : str
    admin : bool
    steward : bool
    reader : bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

def convert_user_to_input_user(user: User) -> InputUser:
    return InputUser(
        user=user.user,
        password=user.hashed_password,
        roles={
            'admin': user.admin,
            'steward': user.steward,
            'reader': user.reader
        }
    )
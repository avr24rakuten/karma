from fastapi import FastAPI, Request, Response, HTTPException, status, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import text

# from typing_extensions import Annotated
import requests
# import time


from lib.mysql import *
from lib.local_class import *
from lib.security import *
from shared.lib.utils import *
from shared.lib.shared_class import *
# from lib.middleware import *

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# creating a FastAPI server
server = FastAPI(title='KARMA API')

#############################################
# MIDDLEWARE APIS
#############################################


#!!!!!!!!!!!! LA DOC SEMBLE NE PLUS S'AFFICHER AVEC le server.middleware ajouté, A CREUSER

# @server.middleware("http") #, include_in_schema=False)
# async def log_requests(request: Request, call_next):
#     start_time = time.perf_counter()
#     response = await call_next(request)
#     background_tasks = BackgroundTasks()
#     background_tasks.add_task(log_api_perf, str(request.url), start_time, response.status_code)
#     return Response(background=background_tasks)

#############################################
# STATUS & HEALTH CHECK SECTION
#############################################

@server.get('/hello', tags=['status'])
async def hello():
    """
    Return Hello Datascientest

    Example
    -------
    curl -X GET -i http://ip_address:port/hello
    """
    return "Hello Datascientest"

@server.get('/status', tags=['status'])
async def get_status():
    """
    Return 1 if API is available

    Example
    -------
    curl -X GET -i http://ip_address:port/status
    """
    return 1

@server.get('/karma_healthcheck', tags=['status'])
async def karma_healthcheck():
    """
    Return in message the unavailable components of Karma app
    
    Example
    -------
    curl -X GET -i http://ip_address:port/karma_healthcheck
    """
    # URLS API status list for all karma app
    api_urls = [
        "http://karma_model:8081/status"
    ]

    status_results = {}

    for api_url in api_urls:
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                status_results[api_url] = "OK"
            else:
                status_results[api_url] = "Unavailable"
        except requests.exceptions.RequestException as e:
            status_results[api_url] = "Failed to connect"

    # Check if karma Database vailable
    status_results['karma_db'] = 'OK' if check_database_connection() else 'Unavailable'

    # Vérifiez si toutes les API sont disponibles
    if all(status == "OK" for status in status_results.values()):
        return {"status": 200, "message": "All Karma Components are OK"}
    else:
        unavailable_comp = [comp for comp, status in status_results.items() if status != "OK"]
        return {"status": 500, "message": f"The following components are not available: {unavailable_comp}"}
        # FAUT-IL RENVOYER UNE ERREUR, JE NE PENSE PAS CAR L'APPEL API EST OK FINALEMENT 
        # raise HTTPException(status_code=400, detail=f"The following components are not available: {unavailable_comp}")

#############################################
# LOGIN SECTION
#############################################

# VERSION AVEC OAuth2 et INPUT Content-Type: application/x-www-form-urlencoded
# @server.post("/users/login", tags=['security'])
# async def login_for_access_token(
#     user_data: Annotated[OAuth2PasswordRequestForm, Depends()],) -> Token:
#     user = authenticate_user(user_data.username, decode_base64(user_data.password))
    # """
    # Get a JWT Token from username and base64 encoded password

    # Parameters
    # ----------
    # user : current user
    # password : base64 encoded user''s password

    # Example
    # -------
    # curl -X POST "http://ip_address:port/users/login" 
    #     -H  "accept: application/json" 
    #     -H  "Content-Type: application/x-www-form-urlencoded" 
    #     -d "username=USER&password=BASE64_PASSWORD"
    # """
    # user = authenticate_user(in_user.username, decode_base64(in_user.password))
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # else:
    #     access_token = create_access_token(
    #         data={"sub": user.user}
    #         # "admin": user.admin, "steward": user.steward, "reader": user.reader}
    #         # ROLES NON EMBARQUES DANS LE TOKEN CAR CELA PEUT CHANGER DURANT LA VIE DU TOKEN
    #         # REMIS EN CAUSE SI TOKEN BLACKLIST
    #     )
    #     return Token(access_token=access_token, token_type="bearer")
    


@server.post("/users/login", tags=['security'])
async def login_for_access_token(in_user: LoginUser) -> Token:
    """
    Get a JWT Token from username and base64 encoded & utf-8 password

    Parameters
    ----------
    user : current user
    password : base64 encoded user''s password

    Example
    -------
    curl -X POST "http://172.26.107.175:8000/users/login" -H "accept: application/json" -H "Content-Type: application/json" -d '{"username":"admin","password":"YWRtaW4="}'
    curl -X POST "http://ip_address:port/users/login" 
        -H  "accept: application/json" 
        -H  "Content-Type: application/json" 
        -d '{"username":"USER","password":"BASE64_PASSWORD"}'
    """
    user = authenticate_user(in_user.username, decode_base64(in_user.password))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        access_token = create_access_token(
            data={"sub": user.user}
            # "admin": user.admin, "steward": user.steward, "reader": user.reader}
            # ROLES NON EMBARQUES DANS LE TOKEN CAR CELA PEUT CHANGER DURANT LA VIE DU TOKEN
            # REMIS EN CAUSE SI TOKEN BLACKLIST
        )
        return Token(access_token=access_token, token_type="bearer")

#############################################
# USERS SECTION
#############################################

@server.post("/users", tags=['users'])
async def create_user(user: InputUser, admin: User = Depends(get_admin)):
    """
    Admin only : User creation from user input. Unprovided roles will lead to a false value for the privilege, 1 role at least is mandatory
    Password is mandatory

    Parameters
    ----------
    user : InputUser class type expected with encoded base64 password

    Example
    -------
    curl -X POST "http://ip_address:port/users" 
        -H  "accept: application/json" 
        -H  "Content-Type: application/json" 
        -H "Authorization: Bearer JWT_TOKEN_VALUE" 
        -d "{\"user\":\"USER\",\"password\":\"BASE64_PASSWORD\",\"roles\":{\"admin\":TRUE/FALSE,\"steward\":TRUE/FALSE,\"reader\":TRUE/FALSE}}"
    """
    if user.roles is None or len(user.roles) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One privilege at least is required for user creation"
        )
    elif not user.password or user.password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is mandatory"
        )
    elif check_user_exist(user.user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    else:
        hashed_password = hash_password(decode_base64(user.password))
        engine = get_engine()
        with engine.connect() as connection:
            sql = "INSERT INTO users (user, hashed_password, "
            sql += ", ".join([f"{role}" for role, status in user.roles.items()])
            sql += ") VALUES (:user, :hashed_password, "
            sql += ", ".join([f"{'true' if status else 'false'}" for role, status in user.roles.items()])
            sql += f")"
            statement = text(sql)
            try:
                connection.execute(statement,{"user": user.user, "hashed_password": hashed_password})
                # Default rollback behavior with alchemy, so commit change !!!!
                connection.commit()
            except ValueError:
                connection.rollback()
                raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur SQL"
                )
        return {"detail": "User successfully created"}

@server.post("/users/reader", tags=['users'])
async def create_user_reader(user: InputUser):
    """
    User, reader only by default, creation from user input. No matter roles provided, created user will be reader role only
    Password is mandatory

    Parameters
    ----------
    user : InputUser class type expected with encoded base64 password

    Example
    -------
    curl -X POST "http://ip_address:port/users/reader" 
        -H  "accept: application/json" 
        -H  "Content-Type: application/json" 
        -H "Authorization: Bearer JWT_TOKEN_VALUE" 
        -d "{\"user\":\"USER\",\"password\":\"BASE64_PASSWORD\"}"
    """
    if not user.password or user.password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is mandatory"
        )
    elif check_user_exist(user.user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    else:
        hashed_password = hash_password(decode_base64(user.password))
        engine = get_engine()
        with engine.connect() as connection:
            sql = "INSERT INTO users (user, hashed_password, admin, steward, reader) VALUES (:user, :hashed_password, false, false, true)"
            statement = text(sql)
            try:
                connection.execute(statement,{"user": user.user, "hashed_password": hashed_password})
                # Default rollback behavior with alchemy, so commit change !!!!
                connection.commit()
            except ValueError:
                connection.rollback()
                raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur SQL"
                )
        return {"detail": "User successfully created"}

#### SI PASSAGE A UN TOKEN BLACKLIST, CETTE API DEVRA EGALEMENT AJOUTER LES TOKEN DES USERS SUPPRIMEES CAR ROLE UPDATED
@server.put("/users", tags=['users'])
async def update_user(user: InputUser, admin: User = Depends(get_admin)):
    """
    Admin only : User''s roles update from provided user. Unprovided roles will not be updated, 1 role at least is mandatory

    Parameters
    ----------
    user : InputUser class type expected with encoded base64 password(unused)

    Example
    -------
    curl -X PUT "http://ip_address:port/users" 
        -H  "accept: application/json" 
        -H  "Content-Type: application/json" 
        -H "Authorization: Bearer JWT_TOKEN_VALUE" 
        -d "{\"user\":\"USER\",\"password\":\"BASE64_PASSWORD\",\"roles\":{\"admin\":TRUE/FALSE,\"steward\":TRUE/FALSE,\"reader\":TRUE/FALSE}}"
    """

    if user.roles is None or len(user.roles) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One role at least is required for user update"
        )
    else:
        engine = get_engine()
        with engine.connect() as connection:
            sql = "UPDATE karma.users SET "
            sql += ", ".join([f"{role} = {'true' if status else 'false'}" for role, status in user.roles.items()])
            sql += f" WHERE user = :user"
            statement = text(sql)
            try:
                connection.execute(statement,{"user": user.user})
                # Default rollback behavior with alchemy, so commit change !!!!
                connection.commit()
            except ValueError:
                connection.rollback()
                raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur SQL"
            )
        return {"detail": "User successfully updated"}

@server.put("/users/password", tags=['users'])
async def update_user_password(user: InputUser, admin: User = Depends(get_admin)):
    """
    Admin only : User''s password update from provided user. base64 encoded password can't be null or empty

    Parameters
    ----------
    user : InputUser class type expected with encoded base64 password(unused)

    Example
    -------
    curl -X PUT "http://ip_address:port/users/password"
        -H  "accept: application/json" 
        -H  "Content-Type: application/json" 
        -H "Authorization: Bearer JWT_TOKEN_VALUE" 
        -d "{\"user\":\"USER\",\"password\":\"BASE64_PASSWORD\",\"roles\":{\"admin\":TRUE/FALSE,\"steward\":TRUE/FALSE,\"reader\":TRUE/FALSE}}"
    """

    if not user.password or user.password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is null or empty"
        )
    else:
        hashed_password = hash_password(decode_base64(user.password))
        engine = get_engine()
        with engine.connect() as connection:
            statement = text('UPDATE karma.users SET hashed_password = :hashed_password WHERE users.user = :user')
            try:
                connection.execute(statement,{"user": user.user, "hashed_password": hashed_password})
                # Default rollback behavior with alchemy, so commit change !!!!
                connection.commit()
            except ValueError:
                connection.rollback()
                raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur SQL"
            )
        return {"detail": "User''s password successfully updated"}


#### SI PASSAGE A UN TOKEN BLACKLIST, CETTE API DEVRA EGALEMENT AJOUTER LES TOKEN DES USERS SUPPRIMEES
@server.delete("/users/{user}", tags=['users'])
async def delete_user(user: str, admin: User = Depends(get_admin)):
    """
    Admin only : User delete

    Parameters
    ----------
    user : user name

    Example
    -------
    curl -X DELETE "http://ip_address:port/users/USER"
        -H "Authorization: Bearer JWT_TOKEN_VALUE" 
    """

    engine = get_engine()
    with engine.connect() as connection:

        select_statement = text('SELECT * FROM users WHERE users.user = :user')
        result = connection.execute(select_statement, {"user": user})
        user_exists = result.fetchone() is not None
        if user_exists:
            statement = text('DELETE FROM users WHERE users.user = :user')
            try:
                connection.execute(statement,{"user": user})
                # Default rollback behavior with alchemy, so commit change !!!!
                connection.commit()
            except ValueError:
                connection.rollback()
                raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SQL Error"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resources not found".format(user)
            )
    return {"detail": "User {} successfully deleted".format(user)}


@server.get('/users/{user_id:int}', response_model=InputUser, tags=['users'])
async def get_user(user_id: int, admin: User = Depends(get_admin)):
    """
    Admin only : Get a type class InputUser from user_id

    Parameters
    ----------
    user : user name

    Example
    -------
    curl -X GET "http://ip_address:port/users/USER_ID"
        -H  "accept: application/json" 
        -H  "Content-Type: application/json" 
        -H "Authorization: Bearer JWT_TOKEN_VALUE"

    Output example
    --------------
    {"user":"USER","password":"EMPTY","roles":{"admin":true/false,"steward":true/false,"reader":true/false}}
    """
    engine = get_engine()
    with engine.connect() as connection:
        statement = text('SELECT user_id, user, hashed_password, admin, steward, reader FROM users WHERE users.user_id = :user_id')
        try:
            results = connection.execute(statement,{"user_id": user_id})
        except ValueError:
            connection.rollback()
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur SQL"
        )

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
        return convert_user_to_input_user(user)
    else:
        raise HTTPException(status_code=404, detail="Resource Not Found : Unknown User ID")



#############################################
# PREDICT SECTION
#############################################

# @server.post("/unsecured/products/predict_image", tags=['predict'])
# async def predict(description: str = Form(...), image: UploadFile = File(...)):

#     if not description:
#         raise HTTPException(status_code=400, detail="Description is mandatory")

#     if image:
#         image_contents = await image.read()
#         image_path = os.path.join("shared/buffer/image", image.filename)
#         with open(image_path, "wb") as f:
#                 f.write(image_contents)

#     item = InputProduct(description=description, image_link=image_path)

#     model_api_url = "http://karma_model:8081/predict"
#     response = requests.post(model_api_url, json=item.dict())
#     if response.status_code != 200:
#         return {"error": f"Failed to get prediction from model API: {response.text}"}
#     prediction = response.json()
#     return {"prediction": prediction}


@server.post("/products/predict", tags=['predict'])
async def predict(description: str = Form(...), image: UploadFile = File(...), any: User = Depends(get_any_role)):
    """
    Admin/Steward/Reader : Get a product category prediction from ML

    Parameters
    ----------
    item : Expected item contains a mandatory description and optionnal image_link

    Example
    -------
    curl -X POST "http://172.26.107.175:8000/products/predict" 
        -H  "accept: application/json" 
        -H  "Content-Type: application/json" 
        -H "Authorization: Bearer JWT_TOKEN_VALUE" 
        -F "description=DESCRIPTION"
        -F "image=@/path/to/image.jpg"

    Output example
    --------------
    {"prediction":1234}
    """
    if not description:
        raise HTTPException(status_code=400, detail="Description is mandatory")
    
    if image:
        image_contents = await image.read()
        image_path = os.path.join("./shared/buffer/image", image.filename)
        with open(image_path, "wb") as f:
                f.write(image_contents)

    item = InputProduct(description=description, image_link=image_path)

    model_api_url = "http://karma_model:8081/predict"
    response = requests.post(model_api_url, json=item.dict())
    if response.status_code != 200:
        return {f"status {str(response.status_code)}": f"Failed to get prediction from model API: {response.text}"}
    prediction = response.json()
    return {"prediction": prediction}


# @server.post("/products/predict", tags=['predict'])
# async def predict(item: InputProduct, any: User = Depends(get_any_role)):
#     """
#     Admin/Steward/Reader : Get a product category prediction from ML

#     Parameters
#     ----------
#     item : Expected item contains a mandatory description and optionnal image_link

#     Example
#     -------
#     curl -X POST "http://172.26.107.175:8000/products/predict" 
#         -H  "accept: application/json" 
#         -H  "Content-Type: application/json" 
#         -H "Authorization: Bearer JWT_TOKEN_VALUE" 
#         -d '{"description":"PRODUCT_DESCRIPTION","image_link":"IMAGE_LINK"}'

#     Output example
#     --------------
#     {"prediction":1234}
#     """
#     # L'image n'est pas obligatoire, à revoir le moment venu !!!!
#     if not item.description:
#         raise HTTPException(status_code=400, detail="Description is mandatory")

#     model_api_url = "http://karma_model:8081/predict"
#     response = requests.post(model_api_url, json=item.dict())
#     if response.status_code != 200:
#         return {"error": f"Failed to get prediction from model API: {response.text}"}
#     prediction = response.json()
#     return {"prediction": prediction}


# @server.get('/users')
# async def get_users():
#     engine = get_engine()
#     with engine.connect() as connection:
#         statement = text('SELECT * FROM users')
#         results = connection.execute(statement)

#     results = [
#         User(
#             user_id=i[0],
#             user=i[1],
#             hashed_password=i[2],
#             admin=i[3],
#             steward=i[4],
#             reader=i[5]
#             ) for i in results.fetchall()]
#     return results



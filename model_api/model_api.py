from fastapi import FastAPI, HTTPException, UploadFile, File #, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from sqlalchemy import text
# from typing_extensions import Annotated
from pydantic import BaseModel
from tensorflow import keras
import json

from lib.model import *
from shared.lib.shared_class import *
# from lib.local_class import *
# from lib.security import *

# creating a FastAPI server
server = FastAPI(title='MODEL API')

# LOADING ON APP START (MORE EFFICIENT)
with open("models/tokenizer_config.json", "r", encoding="utf-8") as json_file:
    tokenizer_config = json_file.read()
tokenizer = keras.preprocessing.text.tokenizer_from_json(tokenizer_config)

lstm = keras.models.load_model("models/best_lstm_model.h5")
vgg16 = keras.models.load_model("models/best_vgg16_model.h5")

with open("models/best_weights.json", "r") as json_file:
    best_weights = json.load(json_file)

with open("models/mapper.json", "r") as json_file:
    mapper = json.load(json_file)

predictor = Predict(
            tokenizer=tokenizer,
            lstm=lstm,
            vgg16=vgg16,
            best_weights=best_weights,
            mapper=mapper,
        )

@server.get('/status')
async def get_status():
    """Returns 1
    """
    return 1

@server.post("/predict")
async def predict(inputProduct: InputProduct):
    try:
        prediction = predictor.predict(inputProduct.description, inputProduct.image_link)
        return {prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
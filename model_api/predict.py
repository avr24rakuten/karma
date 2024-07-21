from features.build_features import TextPreprocessor
import tensorflow as tf
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import json
from tensorflow import keras
# import pandas as pd
# import argparse


###### USE FOR LOCAL TEST ONLY ON MODEL CONTAINER !!!!!!!!




class Predict:
    def __init__(
        self,
        tokenizer,
        lstm,
        vgg16,
        best_weights,
        mapper,
    ):
        self.tokenizer = tokenizer
        self.lstm = lstm
        self.vgg16 = vgg16
        self.best_weights = best_weights
        self.mapper = mapper

    def preprocess_image(self, image_path, target_size):
        img = load_img(image_path, target_size=target_size)
        img_array = img_to_array(img)
        
        img_array = preprocess_input(img_array)
        return img_array

    def predict(self, description, image_path=None):
        text_preprocessor = TextPreprocessor()
        description = text_preprocessor.preprocess_text(description)
        sequences = self.tokenizer.texts_to_sequences([description])
        padded_sequences = pad_sequences(
            sequences, maxlen=10, padding="post", truncating="post"
        )

        if image_path:
            target_size = (224, 224, 3)
            image = self.preprocess_image(image_path, target_size)
            images = tf.convert_to_tensor([image], dtype=tf.float32)
            vgg16_proba = self.vgg16.predict([images])
        else:
            vgg16_proba = 0

        lstm_proba = self.lstm.predict([padded_sequences])

        concatenate_proba = (
            self.best_weights[0] * lstm_proba + self.best_weights[1] * vgg16_proba
        )
        final_prediction = np.argmax(concatenate_proba, axis=1)

        return self.mapper[str(final_prediction[0])]

def main():

    # Configurations and model loading
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

    description = "Olivia: Personalisiertes Notizbuch / 150 Seiten / Punktraster / Ca Din A5 / Rosen-Design"
    # image_path = "data_test/image_1263597046_product_3804725264.jpg"
    image_path = "shared/image_1263597046_product_3804725264.jpg"
    prediction = predictor.predict(description, image_path)
    print(prediction)

if __name__ == "__main__":
    main()
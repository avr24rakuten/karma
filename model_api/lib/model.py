from features.build_features import TextPreprocessor
import tensorflow as tf
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import boto3
import os


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
    

def download_from_s3_folder(bucket_name, s3_folder, local_folder):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    # Créer le dossier local si nécessaire
    os.makedirs(local_folder, exist_ok=True)

    # Télécharger les fichiers
    for obj in bucket.objects.filter(Prefix=s3_folder):
        if not obj.key.endswith('/'): 
            target = os.path.join(local_folder, os.path.relpath(obj.key, s3_folder))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            bucket.download_file(obj.key, target)
            print(f"Downloaded {obj.key} to {target}")
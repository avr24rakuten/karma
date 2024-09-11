import mlflow
import mlflow.keras
import os
import json
import boto3
import pandas as pd
import numpy as np
from sklearn.utils import resample
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator


# Configuration AWS CLI using environment variables
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAW5BDRBJQPYBDSRFU'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
os.environ['AWS_DEFAULT_REGION'] = 'eu-north-1'


def archive_old_models_and_upload_to_s3(local_path, bucket_name, s3_path, archive_path):
    s3 = boto3.client('s3')
    
    # Lister les fichiers existants dans le dossier sur S3
    existing_models = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_path)
    
    if 'Contents' in existing_models:
        # Archiver les fichiers existants en les déplaçant vers ./archived_models
        for file in existing_models['Contents']:
            old_s3_key = file['Key']
            archived_s3_key = old_s3_key.replace(s3_path, archive_path)  # Remplace le chemin pour le dossier d'archive
            s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': old_s3_key}, Key=archived_s3_key)
            s3.delete_object(Bucket=bucket_name, Key=old_s3_key)  # Supprimer l'ancien fichier après copie

    # Upload des nouveaux modèles depuis le local_path
    if os.path.isdir(local_path):
        for root, dirs, files in os.walk(local_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, local_path)
                s3_key = os.path.join(s3_path, relative_path).replace("\\", "/")  # Remplacez les backslashes par des slashes pour S3
                s3.upload_file(file_path, bucket_name, s3_key)
    else:
        s3_key = os.path.join(s3_path, os.path.basename(local_path)).replace("\\", "/")
        s3.upload_file(local_path, bucket_name, s3_key)


def upload_to_s3(local_path, bucket_name, s3_path):
    s3 = boto3.client('s3')
    if os.path.isdir(local_path):
        for root, dirs, files in os.walk(local_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, local_path)
                s3_key = os.path.join(s3_path, relative_path).replace("\\", "/")  # Remplacez les backslashes par des slashes pour S3
                s3.upload_file(file_path, bucket_name, s3_key)
    else:
        s3.upload_file(local_path, bucket_name, s3_path)


def preprocess_image(image_path, target_size):
    from tensorflow.keras.preprocessing import image
    img = image.load_img(image_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array[0]


def save_metrics(metrics, file_path):
    with open(file_path, "w") as f:
        json.dump(metrics, f, indent=4)


def map_prdtypecode(y):
    unique_classes = np.unique(y)
    class_mapping = {cls: idx for idx, cls in enumerate(unique_classes)}
    y_mapped = y.replace(class_mapping)
    return y_mapped, class_mapping


class TextLSTMModel:
    def __init__(self, max_words, max_sequence_length, num_classes):
        self.max_words = max_words
        self.max_sequence_length = max_sequence_length
        self.num_classes = num_classes
        self.tokenizer = Tokenizer(num_words=max_words)
        self.model = None

    def preprocess_and_fit(self, X_train, y_train, X_val, y_val):
        self.tokenizer.fit_on_texts(X_train["description"].astype(str))
        tokenizer_config = self.tokenizer.to_json()
        with open("./models_weight/tokenizer_config.json", "w", encoding="utf-8") as json_file:
            json_file.write(tokenizer_config)

        train_sequences = self.tokenizer.texts_to_sequences(X_train["description"].astype(str))
        val_sequences = self.tokenizer.texts_to_sequences(X_val["description"].astype(str))
        train_padded_sequences = pad_sequences(
            train_sequences,
            maxlen=self.max_sequence_length,
            padding="post",
            truncating="post",
        )
        val_padded_sequences = pad_sequences(
            val_sequences,
            maxlen=self.max_sequence_length,
            padding="post",
            truncating="post",
        )

        text_input = Input(shape=(self.max_sequence_length,))
        embedding_layer = Embedding(input_dim=self.max_words, output_dim=128)(text_input)
        lstm_layer = LSTM(128)(embedding_layer)
        output = Dense(self.num_classes, activation="softmax")(lstm_layer)
        self.model = Model(inputs=[text_input], outputs=output)
        self.model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

        lstm_callbacks = [
            ModelCheckpoint(filepath="./models/best_lstm_model.keras", save_best_only=True),
            EarlyStopping(patience=3, restore_best_weights=True),
            TensorBoard(log_dir="./logs"),
        ]
        self.model.fit(
            train_padded_sequences,
            y_train,
            epochs=10,
            batch_size=32,
            validation_data=(val_padded_sequences, y_val),
            callbacks=lstm_callbacks,
        )

    def save_model(self):
        if self.model:
            self.model.save("./models/final_model.keras")


class ImageVGG16Model:
    def __init__(self, num_classes):
        self.model = None
        self.num_classes = num_classes

    def preprocess_and_fit(self, X_train, y_train, X_val, y_val):
        batch_size = 32

        X_train["filename"] = "image_" + X_train["imageid"].astype(str) + "_product_" + X_train["productid"].astype(str) + ".jpg"
        X_val["filename"] = "image_" + X_val["imageid"].astype(str) + "_product_" + X_val["productid"].astype(str) + ".jpg"
        y_train = y_train.astype(str)
        y_val = y_val.astype(str)

        df_train = pd.concat([X_train, y_train.rename('prdtypecode')], axis=1)
        df_val = pd.concat([X_val, y_val.rename('prdtypecode')], axis=1)

        missing_classes_val = set(df_train['prdtypecode'].unique()) - set(df_val['prdtypecode'].unique())
        for cls in missing_classes_val:
            samples_to_add = df_train[df_train['prdtypecode'] == cls].sample(n=5, replace=True)
            df_val = pd.concat([df_val, samples_to_add])

        missing_classes_train = set(df_val['prdtypecode'].unique()) - set(df_train['prdtypecode'].unique())
        for cls in missing_classes_train:
            samples_to_add = df_val[df_val['prdtypecode'] == cls].sample(n=5, replace=True)
            df_train = pd.concat([df_train, samples_to_add])

        train_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
        train_generator = train_datagen.flow_from_dataframe(
            dataframe=df_train,
            directory="./data/images/images",
            x_col="filename",
            y_col="prdtypecode",
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode="categorical",
            shuffle=True,
        )

        val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
        val_generator = val_datagen.flow_from_dataframe(
            dataframe=df_val,
            directory="./data/images/images",
            x_col="filename",
            y_col="prdtypecode",
            target_size=(224, 224),
            batch_size=batch_size,
            class_mode="categorical",
            shuffle=False,
        )

        image_input = Input(shape=(224, 224, 3))

        vgg16_base = VGG16(include_top=False, weights="imagenet", input_tensor=image_input)

        x = vgg16_base.output
        x = Flatten()(x)
        x = Dense(256, activation="relu")(x)
        output = Dense(self.num_classes, activation="softmax")(x)

        self.model = Model(inputs=vgg16_base.input, outputs=output)

        for layer in vgg16_base.layers:
            layer.trainable = False

        self.model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

        vgg_callbacks = [
            ModelCheckpoint(filepath="./models/best_vgg16_model.keras", save_best_only=True),
            EarlyStopping(patience=3, restore_best_weights=True),
            TensorBoard(log_dir="./logs"),
        ]

        self.model.fit(
            train_generator,
            epochs=10,
            validation_data=val_generator,
            callbacks=vgg_callbacks,
        )


class ConcatenateModel:
    def __init__(self, tokenizer, lstm, vgg16):
        self.tokenizer = tokenizer
        self.lstm = lstm
        self.vgg16 = vgg16

    def predict(self, X_train, y_train, new_samples_per_class=50, max_sequence_length=100):
        num_classes = len(np.unique(y_train))

        new_X_train = pd.DataFrame(columns=X_train.columns)
        new_y_train = pd.DataFrame(columns=['prdtypecode'])

        for class_label in range(num_classes):
            # Vérifiez si y_train est un tableau NumPy ou une Series Pandas
            if isinstance(y_train, pd.Series):
                indices = y_train.index[y_train == class_label].tolist()
            else:  # Si c'est un tableau NumPy
                indices = np.where(y_train == class_label)[0].tolist()

            # Vérifiez que `indices` n'est pas vide avant de faire l'échantillonnage
            if len(indices) > 0:
                if len(indices) >= new_samples_per_class:
                    sampled_indices = resample(indices, n_samples=new_samples_per_class, replace=False, random_state=42)
                else:
                    sampled_indices = resample(indices, n_samples=new_samples_per_class, replace=True, random_state=42)

                new_X_train = pd.concat([new_X_train, X_train.loc[sampled_indices]])
                new_y_train = pd.concat([new_y_train, y_train.loc[sampled_indices]])
            else:
                print(f"Warning: No data found for class {class_label}. Skipping this class.")

        new_X_train = new_X_train.reset_index(drop=True)
        new_y_train = new_y_train.reset_index(drop=True)

        # Vérifiez si new_y_train est un DataFrame avec la colonne 'prdtypecode'
        if 'prdtypecode' in new_y_train:
            # Gérer les NaN dans new_y_train['prdtypecode']
            if new_y_train['prdtypecode'].isnull().sum() > 0:
                print(f"Warning: {new_y_train['prdtypecode'].isnull().sum()} NaN values found in prdtypecode. Filling with mode.")
                new_y_train['prdtypecode'].fillna(new_y_train['prdtypecode'].mode()[0], inplace=True)
            
            # Assurez-vous que la colonne prdtypecode est bien un entier
            new_y_train = new_y_train['prdtypecode'].values.reshape(-1).astype("int")
        else:
            # Si new_y_train n'a pas la colonne 'prdtypecode', afficher une erreur
            raise KeyError("'prdtypecode' column not found in new_y_train DataFrame")

        train_sequences = self.tokenizer.texts_to_sequences(new_X_train["description"].astype(str))
        train_padded_sequences = pad_sequences(train_sequences, maxlen=max_sequence_length, padding="post", truncating="post")

        target_size = (224, 224, 3)
        images_train = new_X_train.apply(lambda row: preprocess_image(f"./data/images/images/image_{row['imageid']}_product_{row['productid']}.jpg", target_size), axis=1)
        images_train = np.array(list(images_train))

        lstm_proba = self.lstm.predict(train_padded_sequences)
        vgg16_proba = self.vgg16.predict(images_train)

        return lstm_proba, vgg16_proba, new_y_train


    def optimize(self, lstm_proba, vgg16_proba, y_train):
        best_weights = None
        best_accuracy = 0.0
        metrics = []

        for lstm_weight in np.linspace(0, 1, 101):
            vgg16_weight = 1.0 - lstm_weight

            combined_predictions = (lstm_weight * lstm_proba) + (vgg16_weight * vgg16_proba)
            final_predictions = np.argmax(combined_predictions, axis=1)

            accuracy = accuracy_score(y_train, final_predictions)
            f1 = f1_score(y_train, final_predictions, average='weighted')
            precision = precision_score(y_train, final_predictions, average='weighted')
            recall = recall_score(y_train, final_predictions, average='weighted')

            metrics.append({
                'lstm_weight': lstm_weight,
                'vgg16_weight': vgg16_weight,
                'accuracy': accuracy,
                'f1_score': f1,
                'precision': precision,
                'recall': recall
            })

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_weights = (lstm_weight, vgg16_weight)

        save_metrics(metrics, "./metrics.json")
        return best_weights, metrics


def compare_and_update_models(client, new_metrics, model_name, new_version, stage="Production"):
    # Récupérer la dernière version en Production
    current_models = client.get_latest_versions(model_name, stages=[stage])
    
    if not current_models:
        # S'il n'y a pas de modèle en production, promotion automatique du nouveau modèle
        print(f"No current {model_name} models in {stage} stage. Promoting new model.")
        client.transition_model_version_stage(name=model_name, version=new_version, stage="Production")
        return True

    current_model_version = current_models[0]
    current_model_metrics = client.get_run(current_model_version.run_id).data.metrics

    # Comparer les nouvelles métriques avec celles du modèle actuel en Production
    is_better = False
    for metric in new_metrics:
        new_value = new_metrics[metric]
        current_value = current_model_metrics.get(metric, 0)

        if new_value > current_value:
            is_better = True
        elif new_value < current_value:
            # Si une seule des métriques est moins bonne, on ne promeut pas le nouveau modèle
            is_better = False
            break

    if is_better:
        # Si le nouveau modèle est meilleur, promotion de celui-ci en Production
        print(f"New {model_name} model version {new_version} is better. Promoting to Production.")
        client.transition_model_version_stage(name=model_name, version=new_version, stage="Production")
        # Archiver l'ancienne version
        client.transition_model_version_stage(name=model_name, version=current_model_version.version, stage="Archived")
    else:
        # Si le nouveau modèle n'est pas meilleur, archiver cette version sans toucher à la Production
        print(f"New {model_name} model version {new_version} is not better. Archiving new version.")
        client.transition_model_version_stage(name=model_name, version=new_version, stage="Archived")

    return is_better


def update_metadata(train_finished, new_model_keep):
    metadata_path = "./train_model_metadata.json"
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        # Assurez-vous que metadata est une liste
        if isinstance(metadata, list) and len(metadata) > 0:
            metadata[0]["train_finished"] = train_finished
            metadata[0]["new_model_keep"] = new_model_keep
        else:
            raise ValueError("Le fichier JSON ne contient pas de données valides.")
        
    else:
        metadata = [{
            "datetime": "0",
            "sent_to_retrain": True,
            "train_finished": train_finished,
            "new_model_keep": new_model_keep
        }]

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)


def main():
    try:
        client = mlflow.tracking.MlflowClient()

        with mlflow.start_run() as run:
            # Charger les données prétraitées
            X_train = pd.read_csv("./data/X_train.csv")
            Y_train = pd.read_csv("./data/y_train.csv")

            # Suppression des NaN dans X_train et Y_train
            X_train.dropna(inplace=True)
            Y_train.dropna(inplace=True)

            # Assurer que les index de X_train et Y_train restent alignés après suppression
            X_train, Y_train = X_train.align(Y_train, join='inner', axis=0)

            if 'prdtypecode' in Y_train.columns:
                Y_train = Y_train['prdtypecode']

            # Mapper les catégories sur une plage continue
            Y_train, class_mapping = map_prdtypecode(Y_train)
            print(f"Class mapping: {class_mapping}")
            num_classes = len(class_mapping)

            # Définir les paramètres du modèle
            max_words = 10000
            max_sequence_length = 100

            # Diviser les données d'entraînement pour la validation
            X_val = X_train.sample(frac=0.2, random_state=42)
            y_val = Y_train.loc[X_val.index]
            X_train = X_train.drop(X_val.index)
            y_train = Y_train.drop(X_val.index)

            # Vérifiez les dimensions de y_train et y_val
            print(f"Dimensions de y_train: {y_train.shape}")
            print(f"Dimensions de y_val: {y_val.shape}")

            # Convertir y_train et y_val en cibles catégorielles
            y_train_categorical = to_categorical(y_train, num_classes=num_classes)
            y_val_categorical = to_categorical(y_val, num_classes=num_classes)

            print(f"Dimensions de y_train_categorical: {y_train_categorical.shape}")
            print(f"Dimensions de y_val_categorical: {y_val_categorical.shape}")

            # Initialiser les modèles
            text_model = TextLSTMModel(max_words=max_words, max_sequence_length=max_sequence_length, num_classes=num_classes)
            image_model = ImageVGG16Model(num_classes=num_classes)

            # Prétraiter et entraîner les modèles
            text_model.preprocess_and_fit(X_train, y_train_categorical, X_val, y_val_categorical)
            image_model.preprocess_and_fit(X_train, y_train, X_val, y_val)  # Notez que y_train et y_val sont passés directement

            # Recharger les modèles pour la concaténation
            lstm_model = text_model.model
            vgg16_model = image_model.model

            concat_model = ConcatenateModel(tokenizer=text_model.tokenizer, lstm=lstm_model, vgg16=vgg16_model)

            # Obtenir les probabilités prédictives
            lstm_proba, vgg16_proba, new_y_train = concat_model.predict(X_train, y_train)

            # Optimiser les poids des modèles
            best_weights, metrics = concat_model.optimize(lstm_proba, vgg16_proba, new_y_train)

            # Sauvegarder les résultats
            save_metrics(best_weights, "./best_weights.json")

            # Enregistrer les modèles avec MLflow
            mlflow.keras.log_model(text_model.model, "text_model")
            mlflow.keras.log_model(image_model.model, "image_model")

            # Log des métriques
            new_metrics = {
                "accuracy": max(m['accuracy'] for m in metrics),
                "f1_score": max(m['f1_score'] for m in metrics),
                "precision": max(m['precision'] for m in metrics),
                "recall": max(m['recall'] for m in metrics),
            }

            for metric_name, metric_value in new_metrics.items():
                mlflow.log_metric(metric_name, metric_value)

            # Enregistrer les modèles dans le registre des modèles
            model_uri_text = f"runs:/{run.info.run_id}/text_model"
            model_uri_image = f"runs:/{run.info.run_id}/image_model"

            # Enregistrer le modèle textuel et obtenir la version
            text_model_version = mlflow.register_model(model_uri=model_uri_text, name="text_model").version

            # Enregistrer le modèle image et obtenir la version
            image_model_version = mlflow.register_model(model_uri=model_uri_image, name="image_model").version

            # Vérifier si les nouveaux modèles sont meilleurs que ceux en production
            text_model_better = compare_and_update_models(client, new_metrics, "text_model", text_model_version)
            image_model_better = compare_and_update_models(client, new_metrics, "image_model", image_model_version)

            if text_model_better:
                client.transition_model_version_stage(name="text_model", version=text_model_version, stage="Production")
                client.transition_model_version_stage(name="text_model", version=text_model_version - 1, stage="Archived")
            else:
                client.transition_model_version_stage(name="text_model", version=text_model_version, stage="Archived")

            if image_model_better:
                client.transition_model_version_stage(name="image_model", version=image_model_version, stage="Production")
                client.transition_model_version_stage(name="image_model", version=image_model_version - 1, stage="Archived")
            else:
                client.transition_model_version_stage(name="image_model", version=image_model_version, stage="Archived")

            # Mise à jour du fichier train_meta_data.json
            new_model_keep = text_model_better or image_model_better
            update_metadata(train_finished=True, new_model_keep=new_model_keep)

            # Téléchargement des fichiers sur le bucket S3
            bucket_name = "my-karma-bucket"
            s3_models_path = "/models"
            s3_archived_models_path = "/archived_models"

            archive_old_models_and_upload_to_s3("./models", bucket_name, s3_models_path, s3_archived_models_path)
            upload_to_s3("./mlruns", bucket_name, "/mlruns")
            upload_to_s3("./models_weight", bucket_name, "/models_weight")
            upload_to_s3("./train_model_metadata.json", bucket_name, "/train_model_metadata.json")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

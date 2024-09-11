import os
import pandas as pd
import shutil
from sklearn.model_selection import train_test_split
import boto3
from dotenv import load_dotenv

load_dotenv('secret.env')

# Configuration AWS CLI 
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_DEFAULT_REGION')

def download_from_s3(bucket_name, s3_key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, s3_key, local_path)
    print(f"Downloaded {s3_key} to {local_path}")

def sync_s3_folder(bucket_name, s3_folder, local_folder):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    
    # Créer le dossier local si nécessaire
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = os.path.join(local_folder, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)
        print(f"Downloaded {obj.key} to {target}")

def load_and_download_all_images(x_train_path, y_train_path, image_dir, output_image_dir, output_data_dir):
    # Charger les données
    X_train = pd.read_csv(x_train_path)
    Y_train = pd.read_csv(y_train_path)

    # Créer les dossiers de sortie pour les images et les données
    if not os.path.exists(output_image_dir):
        os.makedirs(output_image_dir)
    if not os.path.exists(output_data_dir):
        os.makedirs(output_data_dir)

    # Télécharger et copier toutes les images correspondantes aux données
    for _, row in X_train.iterrows():
        image_id = row['imageid']
        product_id = row['productid']
        image_filename = f"image_{image_id}_product_{product_id}.jpg"
        src_s3_key = os.path.join(image_dir, image_filename)
        dst_path = os.path.join(output_image_dir, image_filename)
        
        # Télécharger l'image depuis S3
        if not os.path.exists(dst_path):  # Télécharger uniquement si l'image n'existe pas déjà
            try:
                download_from_s3(bucket_name, src_s3_key, dst_path)
            except Exception as e:
                print(f"Image {image_filename} not found in {image_dir} on S3: {str(e)}")

    # Enregistrer les données dans des fichiers CSV
    x_train_output_path = os.path.join(output_data_dir, 'X_train.csv')
    y_train_output_path = os.path.join(output_data_dir, 'y_train.csv')

    X_train.to_csv(x_train_output_path, index=False)
    Y_train.to_csv(y_train_output_path, index=False)

    return X_train, Y_train

if __name__ == "__main__":

    bucket_name = "my-karma-bucket"

    # Télécharger les dossiers models et mlruns depuis S3
    sync_s3_folder(bucket_name, "models_weight/", "./models_weight")
    sync_s3_folder(bucket_name, "mlruns/", "./mlruns")

    # Téléchargement du fichier train_model_metadata.json depuis S3 dans le dossier models
    download_from_s3(bucket_name, "train_model_metadata.json", "./train_model_metadata.json")
    
    # Téléchargement des datasets depuis S3
    download_from_s3(bucket_name, "csv/X_train.csv", "./data/X_train.csv")
    download_from_s3(bucket_name, "csv/y_train.csv", "./data/y_train.csv")

    # Télécharger toutes les images correspondantes
    X_train, Y_train = load_and_download_all_images(
        "./data/X_train.csv",
        "./data/y_train.csv",
        "images/",  # Le chemin dans S3 où se trouvent les images
        "./data/images/images",
        "./data"
    )
    print("X_train:")
    print(X_train.head())
    print("Y_train:")
    print(Y_train.head())

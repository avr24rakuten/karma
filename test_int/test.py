# import pkg_resources

# def is_installed(package):
#     try:
#         pkg_resources.get_distribution(package)
#         return True
#     except pkg_resources.DistributionNotFound:
#         return False

# packages = ["jose[cryptography]", "passlib[bcrypt]", "python-multipart"]

# for package in packages:
#     if is_installed(package):
#         print(f"Le package {package} est installé.")
#     else:
#         print(f"Le package {package} n'est pas installé.")


# import secrets

# # Générer une clé secrète de 256 bits
# secret_key = secrets.token_hex(32)

# print(secret_key)

# import bcrypt

# # def check_password(password, hashed_password):
# #     # Vérifier si le mot de passe correspond au hachage
# #     return bcrypt.checkpw(password.encode(), hashed_password.encode())

# # print("result is " + str(check_password(password, hashed_password)))

# def hash_password(password):
#     # Générer un sel
#     salt = bcrypt.gensalt()
#     # Hacher le mot de passe avec le sel
#     hashed_password = bcrypt.hashpw(password.encode(), salt)
#     return hashed_password.decode() 

# hashed_password = hash_password("arnaud")
# print(hashed_password)

# import base64

# def encode_base64(str_variable):
#     str_variable_bytes = str_variable.encode('utf-8')
#     str_variable_base64 = base64.b64encode(str_variable_bytes)
#     return str_variable_base64.decode('utf-8')

# def decode_base64(str_variable_base64):
#     str_variable_base64_bytes = str_variable_base64.encode('utf-8')
#     str_variable_bytes = base64.b64decode(str_variable_base64_bytes)
#     return str_variable_bytes.decode('utf-8')

# print(encode_base64('arnaud'))
# print(decode_base64('YXJuYXVk'))

# import requests

# url = "http://172.26.107.175:8000/products/predict"
# token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyMjgyMjkyMX0.P1Nt8P-ysPxkY_nJrE3uEAzuoKqSDgnRbEQqHDv6h68"

# headers = {
#     "accept": "application/json",
#     "Authorization": f"Bearer {token}"
# }

# files = {
#     "description": (None, "Olivia: Personalisiertes Notizbuch / 150 Seiten / Punktraster / Ca Din A5 / Rosen-Design"),
#     "image": ("image_1263597046_product_3804725264.jpg", open("image_1263597046_product_3804725264.jpg", "rb"), "image/jpeg")
# }

# response = requests.post(url, headers=headers, files=files)

# print(response.text)
########################################################################################
# import os
# import json
# import sys
# import requests

# url = "http://{}:8000/products/predict".format('172.26.107.175')
# headers = {
#     "accept": "application/json",
#     "Authorization": "Bearer {}".format('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyMjk3ODgyOX0.LplANs1QjaMGmXL8QNE-_iiU1ojreqEsur0vR68wdAQ'),
# }
# # image_path = "image_1263597046_product_3804725264.jpg"
# image_url = "https://drive.google.com/file/d/1_DnPZkC83nEcqUaqyWxy-75LBE0-lHyT"
# response_image = requests.get(image_url)
# print(response_image.status_code)
# print(response_image.request)


# # # Vérifier si l'image existe
# # assert os.path.exists(image_path), "L'image n'existe pas à l'emplacement spécifié."

# with open(image_path, "rb") as image_file:
#     files = {
#         "description": (None, "Olivia: Personalisiertes Notizbuch / 150 Seiten / Punktraster / Ca Din A5 / Rosen-Design"),
#         "image": (image_path, image_file, "image/jpeg")
#     }
#     response = requests.post(url, headers=headers, files=files)


# print(response.status_code)
# print(response.request)
# print(response.json())
# print(response.json()['prediction'][0])
############################################################################################################
# url = "http://{}:8000/users/reader".format('172.26.107.175')
# headers = {
#     "accept": "application/json",
#     "Content-Type": "application/json",
#     "Authorization": "Bearer {}".format('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyMjk3ODgyOX0.LplANs1QjaMGmXL8QNE-_iiU1ojreqEsur0vR68wdAQ'),
# }
# data = {
#     "user": "{}".format('test_reader'),
#     "password": "{}".format('dGVzdF9yZWFkZXI='),
#     "roles": {}
# }
# response = requests.post(url, headers=headers, data=json.dumps(data))
# print(response.status_code)
# print(response.request)
# print(response._content)

# check_url = "http://{}:8000/users/login".format('172.26.107.175')
# check_headers = {
#     "accept": "application/json",
#     "Content-Type": "application/json",
# }
# check_data = {
#     "username": 'test_reader',
#     "password": 'dGVzdF9yZWFkZXI=',
# }
# check_response = requests.post(check_url, headers=check_headers, data=json.dumps(check_data))
# print(check_response.status_code)
# print(check_response.request)
# print(check_response._content)


########################################################
# PREDICT VERSION IMAGE HTTP
########################################################

import requests
import os


url = "http://{}:8000/products/predict".format('172.26.107.175')
headers = {
    "accept": "application/json",
    "Authorization": "Bearer {}".format('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTgwNDkyNH0.KZ1QMyfEcCmi1NmkcW_jaJsHsudriIZPjmHY4EGWHvI'),
}

image_url="https://drive.google.com/uc?export=download&id=1_DnPZkC83nEcqUaqyWxy-75LBE0-lHyT"

# image_url = "https://drive.google.com/file/d/1_DnPZkC83nEcqUaqyWxy-75LBE0-lHyT"
response_image = requests.get(image_url)
print(response_image.status_code)
print(response_image.request)

files = {
    "description": (None, "Olivia: Personalisiertes Notizbuch / 150 Seiten / Punktraster / Ca Din A5 / Rosen-Design"),
    "image": ("image.jpg", response_image.content, "image/jpeg")
}
response = requests.post(url, headers=headers, files=files)
print(response.status_code)
print(response.request)
print(response._content)

